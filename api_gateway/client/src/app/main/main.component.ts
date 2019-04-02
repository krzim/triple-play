import { Component, OnInit, OnDestroy } from '@angular/core';
import { NgbModal, NgbModalRef } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { plainToClass } from 'class-transformer';

import { MessagesModalComponent } from '../messages/messages.modal.component';

import { MainService } from './main.service';
import { AuthService } from '../auth/auth.service';
import { UtilitiesService } from '../utilities.service';

import { MessageUpdate } from '../models/message/messageUpdate';
import { MessageListing } from '../models/message/messageListing';
// import { Message } from '../models/message/message';
import { GenericObject } from '../models/genericObject';
import { DashboardService } from '../dashboards/dashboard.service';
import { Dashboard } from '../models/dashboard/dashboard';

const MAX_READ_MESSAGES = 5;
const MAX_TOTAL_MESSAGES = 20;

@Component({
	selector: 'main-component',
	templateUrl: './main.html',
	styleUrls: [
		'./main.scss',
	],
	providers: [MainService, AuthService, UtilitiesService],
})
export class MainComponent implements OnInit, OnDestroy {
	currentUser: string;
	dashboards: Dashboard[] = [];
	messageListings: MessageListing[] = [];
	messageModalRef: NgbModalRef;
	newMessagesCount: number = 0;
	notificationRelativeTimes: GenericObject = {};
	eventSource: any;

	constructor(
		private mainService: MainService, private authService: AuthService,
		private modalService: NgbModal, private toastrService: ToastrService,
		public utils: UtilitiesService, private dashboardService: DashboardService
	) {
		/* Hack along with styles.scss for modal animations in ng-bootstrap */
		NgbModalRef.prototype['c'] = NgbModalRef.prototype.close;
        NgbModalRef.prototype.close = function (reason: string) {
            document.querySelector('.modal-backdrop').classList.remove('show');
            document.querySelector('.modal.show').classList.remove('show');
            setTimeout(() => {
                this['c'](reason);
            }, 250);
        };
        NgbModalRef.prototype['d'] = NgbModalRef.prototype.dismiss;
        NgbModalRef.prototype.dismiss = function (reason: string) {
			document.querySelector('.modal-backdrop').classList.remove('show');
			document.querySelector('.modal.show').classList.remove('show');
            setTimeout(() => {
                this['d'](reason);
            }, 250);
        };
	}

	/**
	 * On init, set the current user from our JWT.
	 * Get a list of interface names that are installed. Get initial notifications for display.
	 * Set up an SSE for handling new notifications.
	 */
	ngOnInit(): void {

		this.currentUser = this.authService.getAndDecodeAccessToken().user_claims.username;
		this.dashboardService.dashboardsChange.subscribe(dashboards => this.dashboards = dashboards);
		// this.getInitialNotifications();
		// this.getNotificationsSSE();
	}

	/**
	 * Closes our SSEs on component destroy.
	 */
	ngOnDestroy(): void {
		if (this.eventSource && this.eventSource.close) { this.eventSource.close(); }
	}

	/**
	 * Grabs a list of message listings for unread notifications (or some amount of read notifications).
	 */
	getInitialNotifications(): void {
		this.mainService.getInitialNotifications()
			.then(messageListings => {
				this.messageListings = messageListings.concat(this.messageListings);
				this._recalculateNewMessagesCount();
			})
			.catch(e => this.toastrService.error(`Error retrieving notifications: ${e.message}`));
	}

	/**
	 * Sets up an SSE for notifications. On new messages, add a notification to the notifications dropdown.
	 * For existing messages, if they were responded to, remove the ! icon.
	 */
	getNotificationsSSE(): void {
		this.authService.getEventSource('/api/streams/messages/notifications')
			.then(eventSource => {
				this.eventSource = eventSource;

				this.eventSource.addEventListener('created', (message: any) => {
					const newMessage = plainToClass(MessageListing, (JSON.parse(message.data) as object));

					const existingMessage = this.messageListings.find(m => m.id === newMessage.id);
					const index = this.messageListings.indexOf(existingMessage);
					// If an existing message exists, replace it with the incoming message. Otherwise add it to the top of the array.
					if (index > -1) {
						this.messageListings[index] = newMessage;
					} else {
						this.messageListings.unshift(newMessage);
					}

					// Remove the oldest message that is read if we have too many (>5) read messages or too many total (>20)
					if (this.messageListings.filter(m => m.is_read).length > MAX_READ_MESSAGES || 
						this.messageListings.length > MAX_TOTAL_MESSAGES) {
						this.messageListings.pop();
					}

					this._recalculateNewMessagesCount();
					this.recalculateRelativeTimes();
				});
				// TODO: re-enable this if we can figure out why componentInstance is throwing an error on get
				// eventSource.addEventListener('read', (message: any) => {
				// const update = plainToClass(MessageUpdate, (JSON.parse(message.data) as object));

				// 	if (!this.messageModalRef || !this.messageModalRef.componentInstance) { return; }

				// 	if (this.messageModalRef.componentInstance.message.id === update.id) {
				// 		(this.messageModalRef.componentInstance.message as Message).read_by.push(update.username);
				// 	}
				// });
				this.eventSource.addEventListener('responded', (message: any) => {
					const update = plainToClass(MessageUpdate, (JSON.parse(message.data) as object));

					const existingMessage = this.messageListings.find(m => m.id === update.id);

					if (existingMessage) {
						existingMessage.awaiting_response = false;
					}

					// TODO: re-enable this if we can figure out why componentInstance is throwing an error on get
					// if (!this.messageModalRef || !this.messageModalRef.componentInstance) { return; }

					// if (this.messageModalRef.componentInstance.message.id === update.id) {
					// 	(this.messageModalRef.componentInstance.message as Message).responded_at = update.timestamp;
					// 	(this.messageModalRef.componentInstance.message as Message).responded_by = update.username;
					// 	(this.messageModalRef.componentInstance.message as Message).awaiting_response = false;
					// }
				});
			});
	}

	/**
	 * Calls the auth service logout method and redirects to login
	 * TODO: should likely roll login into the main component so we don't need to do the location.href.
	 */
	logout(): void {
		this.authService.logout()
			.then(() => location.href = '/login')
			.catch(e => console.error(e));
	}

	/**
	 * Gets the full message detail from the server and displays the message in a new modal.
	 * @param event JS event fired from clicking the message link
	 * @param messageListing Message Listing object to query.
	 */
	openMessage(event: Event, messageListing: MessageListing): void {
		event.preventDefault();

		this.mainService.getMessage(messageListing.id)
			.then(message => {
				messageListing.is_read = true;
				messageListing.last_read_at = this.utils.getCurrentIsoString();
				this._recalculateNewMessagesCount();

				this.messageModalRef = this.modalService.open(MessagesModalComponent);
				
				this.messageModalRef.componentInstance.message = this.utils.cloneDeep(message);
		
				this._handleModalClose(this.messageModalRef);
			})
			.catch(e => this.toastrService.error(`Error opening message: ${e.message}`));
	}

	/**
	 * Recalculates the relative times displayed for notifications (e.g. "a minute ago").
	 * Called when a new message is received and every time the notifications dropdown is opened/closed.
	 */
	recalculateRelativeTimes(): void {
		this.messageListings.forEach(ml => {
			this.notificationRelativeTimes[ml.id] = this.utils.getRelativeLocalTime(ml.created_at);
		});
	}

	/**
	 * Recalculates the number of new notifications to display.
	 */
	private _recalculateNewMessagesCount(): void {
		this.newMessagesCount = this.messageListings.filter(m => !m.is_read).length;
	}

	/**
	 * Doesn't do anything if the message modal is closed normally. Shows an error if the modal is dismissed erroneously.
	 * @param modalRef Modal reference that is being closed
	 */
	private _handleModalClose(modalRef: NgbModalRef): void {
		modalRef.result
			.then((result) => null,
			(error) => { if (error) { this.toastrService.error(error.message); } });
	}
}
