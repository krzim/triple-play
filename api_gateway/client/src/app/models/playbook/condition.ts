import { Type } from 'class-transformer';

import { Transform } from './transform';
import { Argument } from './argument';
import { ExecutionElement } from './executionElement';

export class Condition extends ExecutionElement {
	// _node_id?: number;
	// _branch_id?: number;
	app_name: string;

	action_name: string;

	is_negated: boolean;

	@Type(() => Argument)
	arguments: Argument[] = [];

	@Type(() => Transform)
	transforms: Transform[] = [];

	get all_errors(): string[] {
		return this.errors
				   .concat(...this.arguments.map(argument => argument.all_errors))
				   .concat(...this.transforms.map(transform => transform.all_errors))
	}
}
