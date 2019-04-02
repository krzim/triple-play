import pytest
import json
import requests
import logging

from flask_jwt_extended import decode_token, JWTManager

from api_gateway.appgateway.apiutil import InvalidParameter
from api_gateway.appgateway.validator import validate_parameter, validate_parameters, convert_json

logger = logging.getLogger(__name__)

@pytest.fixture(scope='function')
def message():
	yield 'app1 action1'

def test_validate_parameter_primitive_no_formats_not_required_valid_string(message):
    parameter_api = {'name': 'name1', 'type': 'string'}
    value = 'test string'
    assert validate_parameter(value, parameter_api, message) == value
    value = ''
    assert validate_parameter(value, parameter_api, message) == value

def test_validate_parameter_primitive_no_formats_not_required_valid_number(message):
    parameter_api = {'name': 'name1', 'type': 'number'}
    value = '3.27'
    assert validate_parameter(value, parameter_api, message) == 3.27

def test_validate_parameter_primitive_no_formats_not_required_valid_negative_number(message):
	parameter_api = {'name': 'name1', 'type': 'number'}
	value = '-3.27'
	assert validate_parameter(value, parameter_api, message) == -3.27

def test_validate_parameter_primitive_no_formats_not_required_valid_int(message):
    parameter_api = {'name': 'name1', 'type': 'integer'}
    value = '3'
    assert validate_parameter(value, parameter_api, message) == 3

def test_validate_parameter_primitive_no_formats_not_required_valid_int_from_float(message):
    parameter_api = {'name': 'name1', 'type': 'integer'}
    value = 3.27
    assert validate_parameter(value, parameter_api, message) == 3

def test_validate_parameter_primitive_no_formats_not_required_valid_negative_int(message):
    parameter_api = {'name': 'name1', 'type': 'integer'}
    value = '-3'
    assert validate_parameter(value, parameter_api, message) == -3

def test_validate_parameter_primitive_user(message):
    parameter_api = {'name': 'name1', 'type': 'user'}
    value = '3'
    assert validate_parameter(value, parameter_api, message) == 3

def test_validate_parameter_primitive_role(message):
	parameter_api = {'name': 'name1', 'type': 'role'}
	value = '42'
	assert validate_parameter(value, parameter_api, message) == 42

def test_validate_parameter_primitive_no_formats_not_required_valid_bool(message):
    parameter_api = {'name': 'name1', 'type': 'boolean'}
    true_values = ['true', 'True', 'TRUE', 'TrUe']
    false_values = ['false', 'False', 'FALSE', 'FaLSe']
    for true_value in true_values:
        assert validate_parameter(true_value, parameter_api, message) == True
    for false_value in false_values:
        assert validate_parameter(false_value, parameter_api, message) == False

def test_validate_parameter_primitive_no_formats_required_string(message):
    parameter_api = {'name': 'name1', 'type': 'string', 'required': True}
    value = 'test string'
    assert validate_parameter(value, parameter_api, message) == value
    value = ''
    assert validate_parameter(value, parameter_api, message) == value

def test_validate_parameter_primitive_no_formats_required_none(message):
    parameter_apis = [{'name': 'name1', 'type': 'string', 'required': True},
                      {'name': 'name1', 'type': 'number', 'required': True},
                      {'name': 'name1', 'type': 'integer', 'required': True},
                      {'name': 'name1', 'type': 'boolean', 'required': True}]
    for parameter_api in parameter_apis:
        with pytest.raises(Exception):
            validate_parameter(None, parameter_api, message)

def test_validate_parameter_primitive_not_required_none(message):
    parameter_apis = [{'name': 'name1', 'type': 'string', 'required': False},
                      {'name': 'name1', 'type': 'number', 'required': False},
                      {'name': 'name1', 'type': 'integer'},
                      {'name': 'name1', 'type': 'boolean'}]
    for parameter_api in parameter_apis:
        assert validate_parameter(None, parameter_api, message) == None

def test_validate_parameter_primitive_no_formats_invalid_number(message):
    parameter_api = {'name': 'name1', 'type': 'number'}
    value = 'abc'
    with pytest.raises(Exception):
        validate_parameter(value, parameter_api, message)

def test_validate_parameter_primitive_no_formats_invalid_integer_cause_string(message):
    parameter_api = {'name': 'name1', 'type': 'integer'}
    value = 'abc'
    with pytest.raises(Exception):
        validate_parameter(value, parameter_api, message)

def test_validate_parameter_primitive_no_formats_invalid_user_cause_string(message):
    parameter_api = {'name': 'name1', 'type': 'user'}
    value = 'abc'
    with pytest.raises(Exception):
        validate_parameter(value, parameter_api, message)

def test_validate_parameter_primitive_no_formats_invalid_role_cause_string(message):
    parameter_api = {'name': 'name1', 'type': 'role'}
    value = 'admin'
    with pytest.raises(Exception):
        validate_parameter(value, parameter_api, message)

def test_validate_parameter_primitive_no_formats_invalid_user_cause_0(message):
    parameter_api = {'name': 'name1', 'type': 'user'}
    value = '0'
    with pytest.raises(Exception):
        validate_parameter(value, parameter_api, message)

def test_validate_parameter_primitive_no_formats_invalid_role_cause_0(message):
    parameter_api = {'name': 'name1', 'type': 'role'}
    value = '0'
    with pytest.raises(Exception):
        validate_parameter(value, parameter_api, message)

def test_validate_parameter_primitive_no_formats_invalid_integer_cause_float_string(message):
    parameter_api = {'name': 'name1', 'type': 'integer'}
    value = '3.27'
    with pytest.raises(Exception):
        validate_parameter(value, parameter_api, message)

def test_validate_parameter_primitive_no_formats_invalid_boolean(message):
    parameter_api = {'name': 'name1', 'type': 'boolean'}
    value = 'abc'
    with pytest.raises(Exception):
        validate_parameter(value, parameter_api, message)

def test_validate_parameter_primitive_string_format_valid(message):
    parameter_api = {'name': 'name1', 'type': 'string', 'minLength': 1, 'maxLength': 25}
    value = 'test string'
    assert validate_parameter(value, parameter_api, message) == value

def test_validate_parameter_primitive_string_format_enum_valid(message):
    parameter_api = {'name': 'name1', 'type': 'string', 'minLength': 1, 'maxLength': 25, 'enum': ['test', 'test3']}
    value = 'test'
    assert validate_parameter(value, parameter_api, message) == value

def test_validate_parameter_primitive_string_format_invalid(message):
    parameter_api = {'name': 'name1', 'type': 'string', 'minLength': 1, 'maxLength': 3}
    value = 'test string'
    with pytest.raises(Exception):
        validate_parameter(value, parameter_api, message)

def test_validate_parameter_primitive_string_format_enum_invalid(message):
    parameter_api = {'name': 'name1', 'type': 'string', 'minLength': 1, 'maxLength': 25, 'enum': ['test', 'test3']}
    value = 'test2'
    with pytest.raises(Exception):
        validate_parameter(value, parameter_api, message)

def test_validate_parameter_object(message):
    parameter_api = {
        'name': 'name1',
        'schema': {'type': 'object',
                   'required': ['a', 'b'],
                   'properties':
                       {'a': {'type': 'number'},
                        'b': {'type': 'string'},
                        'c': {'type': 'boolean'}}}}
    value = {'a': 435.6, 'b': 'aaaa', 'c': True}
    validate_parameter(value, parameter_api, message)

def test_validate_parameter_object_from_string(message):
    parameter_api = {
        'name': 'name1',
        'schema': {'type': 'object',
                   'required': ['a', 'b'],
                   'properties':
                       {'a': {'type': 'number'},
                        'b': {'type': 'string'},
                        'c': {'type': 'boolean'}}}}
    value = json.dumps({'a': 435.6, 'b': 'aaaa', 'c': True})
    validate_parameter(value, parameter_api, message)

def test_validate_parameter_object_invalid(message):
    parameter_api = {
        'name': 'name1',
        'schema': {'type': 'object',
                   'required': ['a', 'b'],
                   'properties':
                       {'a': {'type': 'number'},
                        'b': {'type': 'string'},
                        'c': {'type': 'boolean'}}}}
    value = {'a': 435.6, 'invalid': 'aaaa', 'c': True}
    with pytest.raises(Exception):
        validate_parameter(value, parameter_api, message)

def test_validate_parameter_object_array(message):
    parameter_api = {
        'name': 'name1',
        'schema': {'type': 'array',
                   'items': {'type': 'object',
                             'properties': {'A': {'type': 'string'},
                                            'B': {'type': 'integer'}}}
                   }}
    value = [{'A': 'string in', 'B': '33'}, {'A': 'string2', 'B': '7'}]
    validate_parameter(value, parameter_api, message)

def test_validate_parameter_object_array_invalid(message):
    parameter_api = {
        'name': 'name1',
        'schema': {'type': 'array',
                   'items': {'type': 'object',
                             'properties': {'A': {'type': 'string'},

                                            'B': {'type': 'integer'}}}
                   }}
    value = [{'A': 'string in', 'B': '33'}, {'A': 'string2', 'B': 'invalid'}]
    with pytest.raises(Exception):
        validate_parameter(value, parameter_api, message)

def test_validate_parameter_invalid_data_type(message):
    parameter_api = {'name': 'name1', 'type': 'invalid', 'minLength': 1, 'maxLength': 25, 'enum': ['test', 'test3']}
    value = 'test2'
    with pytest.raises(Exception):
        validate_parameter(value, parameter_api, message)

# def test_validate_parameters_all_valid_no_defaults(message):
#     parameter_apis = [
#         {'name': 'name1', 'type': 'string', 'minLength': 1, 'maxLength': 25, 'enum': ['test', 'test3']},
#         {'name': 'name2', 'type': 'integer', 'minimum': -3, 'maximum': 25},
#         {'name': 'name3', 'type': 'number', 'minimum': -10.5, 'maximum': 30.725}]
#     arguments = [Argument('name1', value='test'),
#                  Argument('name2', value='5'),
#                  Argument('name3', value='10.2378')]
#     expected = {'name1': 'test', 'name2': 5, 'name3': 10.2378}
#     message.assertDictEqual(validate_parameters(parameter_apis, arguments, message), expected)

# def test_validate_parameters_invalid_no_defaults(message):
#     parameter_apis = [
#         {'name': 'name1', 'type': 'string', 'minLength': 1, 'maxLength': 25, 'enum': ['test', 'test3']},
#         {'name': 'name2', 'type': 'integer', 'minimum': -3, 'maximum': 25},
#         {'name': 'name3', 'type': 'number', 'minimum': -10.5, 'maximum': 30.725}]
#     arguments = [Argument('name1', value='test'),
#                  Argument('name2', value='5'),
#                  Argument('name3', value='-11.2378')]
#     with pytest.raises(Exception):
#         validate_parameters(parameter_apis, arguments, message)

# def test_validate_parameters_missing_with_valid_default(message):
#     parameter_apis = [
#         {'name': 'name1', 'type': 'string', 'minLength': 1, 'maxLength': 25, 'enum': ['test', 'test3']},
#         {'name': 'name2', 'type': 'integer', 'minimum': -3, 'maximum': 25},
#         {'name': 'name3', 'type': 'number', 'minimum': -10.5, 'maximum': 30.725, 'default': 10.25}]
#     arguments = [Argument('name1', value='test'),
#                  Argument('name2', value='5')]
#     expected = {'name1': 'test', 'name2': 5, 'name3': 10.25}
#     message.assertDictEqual(validate_parameters(parameter_apis, arguments, message), expected)

# def test_validate_parameters_missing_with_invalid_default(message):
#     parameter_apis = [
#         {'name': 'name1', 'type': 'string', 'minLength': 1, 'maxLength': 25, 'enum': ['test', 'test3']},
#         {'name': 'name2', 'type': 'integer', 'minimum': -3, 'maximum': 25},
#         {'name': 'name3', 'type': 'number', 'minimum': -10.5, 'maximum': 30.725, 'default': 'abc'}]
#     arguments = [Argument('name1', value='test'),
#                  Argument('name2', value='5')]
#     expected = {'name1': 'test', 'name2': 5, 'name3': 'abc'}
#     message.assertDictEqual(validate_parameters(parameter_apis, arguments, message), expected)

# def test_validate_parameters_missing_without_default(message):
#     parameter_apis = [
#         {'name': 'name1', 'type': 'string', 'minLength': 1, 'maxLength': 25, 'enum': ['test', 'test3']},
#         {'name': 'name2', 'type': 'integer', 'minimum': -3, 'maximum': 25},
#         {'name': 'name3', 'type': 'number', 'minimum': -10.5, 'maximum': 30.725}]
#     arguments = [Argument('name1', value='test'),
#                  Argument('name2', value='5')]
#     expected = {'name1': 'test', 'name2': 5, 'name3': None}
#     message.assertAlmostEqual(validate_parameters(parameter_apis, arguments, message), expected)

# def test_validate_parameters_missing_required_without_default(message):
#     parameter_apis = [
#         {'name': 'name1', 'type': 'string', 'minLength': 1, 'maxLength': 25, 'enum': ['test', 'test3']},
#         {'name': 'name2', 'type': 'integer', 'minimum': -3, 'maximum': 25},
#         {'name': 'name3', 'type': 'number', 'required': True, 'minimum': -10.5, 'maximum': 30.725}]
#     arguments = [Argument('name1', value='test'),
#                  Argument('name2', value='5')]
#     with pytest.raises(Exception):
#         validate_parameters(parameter_apis, arguments, message)

# def test_validate_parameters_too_many_inputs(message):
#     parameter_apis = [
#         {'name': 'name1', 'type': 'string', 'minLength': 1, 'maxLength': 25, 'enum': ['test', 'test3']},
#         {'name': 'name2', 'type': 'integer', 'minimum': -3, 'maximum': 25}]
#     arguments = [Argument('name1', value='test'),
#                  Argument('name2', value='5'),
#                  Argument('name3', value='-11.2378')]
#     with pytest.raises(Exception):
#         validate_parameters(parameter_apis, arguments, message)

# def test_validate_parameters_skip_action_references(message):
#     parameter_apis = [
#         {'name': 'name1', 'type': 'string', 'minLength': 1, 'maxLength': 25, 'enum': ['test', 'test3']},
#         {'name': 'name2', 'type': 'integer', 'minimum': -3, 'maximum': 25},
#         {'name': 'name3', 'type': 'number', 'required': True, 'minimum': -10.5, 'maximum': 30.725}]
#     arguments = [Argument('name1', value='test'),
#                  Argument('name2', value='5'),
#                  Argument('name3', reference='action1')]
#     expected = {'name1': 'test', 'name2': 5}
#     message.assertDictEqual(validate_parameters(parameter_apis, arguments, message), expected)

# def test_validate_parameters_skip_action_references_inputs_non_string(message):
#     parameter_apis = [
#         {'name': 'name1', 'type': 'string', 'minLength': 1, 'maxLength': 25, 'enum': ['test', 'test3']},
#         {'name': 'name2', 'type': 'integer', 'minimum': -3, 'maximum': 25},
#         {'name': 'name3', 'type': 'number', 'required': True, 'minimum': -10.5, 'maximum': 30.725}]
#     arguments = [Argument('name1', value='test'),
#                  Argument('name2', value=5),
#                  Argument('name3', reference='action1')]
#     expected = {'name1': 'test', 'name2': 5}
#     message.assertDictEqual(validate_parameters(parameter_apis, arguments, message), expected)

def test_convert_json(message):
    parameter_api = {
        'name': 'name1',
        'schema': {'type': 'object',
                   'required': ['a', 'b'],
                   'properties':
                       {'a': {'type': 'number'},
                        'b': {'type': 'string'},
                        'c': {'type': 'boolean'}}}}
    value = {'a': '435.6', 'b': 'aaaa', 'c': 'true'}
    converted = convert_json(parameter_api, value, message)
    assert converted == {'a': 435.6, 'b': 'aaaa', 'c': True}

def test_convert_json_invalid(message):
    parameter_api = {
        'name': 'name1',
        'schema': {'type': 'object',
                   'required': ['a', 'b'],
                   'properties':
                       {'a': {'type': 'number'},
                        'b': {'type': 'string'},
                        'c': {'type': 'boolean'}}}}
    value = {'a': '435.6', 'b': 'aaaa', 'c': 'invalid'}
    with pytest.raises(Exception):
        convert_json(parameter_api, value, message)

def test_convert_json_nested(message):
    parameter_api = {
        'name': 'name1',
        'schema': {'type': 'object',
                   'required': ['a', 'b'],
                   'properties':
                       {'a': {'type': 'number'},
                        'b': {'type': 'string'},
                        'c': {'type': 'object',
                              'properties': {'A': {'type': 'string'},
                                             'B': {'type': 'integer'}}}}}}
    value = {'a': '435.6', 'b': 'aaaa', 'c': {'A': 'string in', 'B': '3'}}
    converted = convert_json(parameter_api, value, message)
    assert converted == {'a': 435.6, 'b': 'aaaa', 'c': {'A': 'string in', 'B': 3}}

def test_convert_json_nested_invalid(message):
    parameter_api = {
        'name': 'name1',
        'schema': {'type': 'object',
                   'required': ['a', 'b'],
                   'properties':
                       {'a': {'type': 'number'},
                        'b': {'type': 'string'},
                        'c': {'type': 'object',
                              'properties': {'A': {'type': 'string'},
                                             'B': {'type': 'integer'}}}}}}
    value = {'a': '435.6', 'b': 'aaaa', 'c': {'A': 'string in', 'B': 'invalid'}}
    with pytest.raises(Exception):
        convert_json(parameter_api, value, message)

def test_convert_primitive_array(message):
    parameter_api = {
        'name': 'name1',
        'schema': {'type': 'array',
                   'items': {'type': 'number'}}}
    value = ['1.3', '3.4', '555.1', '-132.2']
    converted = convert_json(parameter_api, value, message)
    assert converted == [1.3, 3.4, 555.1, -132.2]

def test_convert_primitive_array_invalid(message):
    parameter_api = {
        'name': 'name1',
        'schema': {'type': 'array',
                   'items': {'type': 'number'}}}
    value = ['1.3', '3.4', '555.1', 'invalid']
    with pytest.raises(Exception):
        convert_json(parameter_api, value, message)

def test_convert_object_array(message):
    parameter_api = {
        'name': 'name1',
        'schema': {'type': 'array',
                   'items': {
                       'type': 'object',
                       'properties': {'A': {'type': 'string'},
                                      'B': {'type': 'integer'}}}
                   }}
    value = [{'A': 'string in', 'B': '33'}, {'A': 'string2', 'B': '7'}]
    expected = [{'A': 'string in', 'B': 33}, {'A': 'string2', 'B': 7}]
    converted = convert_json(parameter_api, value, message)
    assert len(converted) == len(expected) 
    for i in range(len(converted)):
        assert converted[i] == expected[i]

def test_convert_object_array_invalid(message):
    parameter_api = {
        'name': 'name1',
        'schema': {'type': 'array',
                   'items': {
                       'type': 'object',
                       'properties': {'A': {'type': 'string'},
                                      'B': {'type': 'integer'}}}
                   }}
    value = [{'A': 'string in', 'B': '33'}, {'A': 'string2', 'B': 'invalid'}]
    with pytest.raises(Exception):
        convert_json(parameter_api, value, message)

def test_convert_object_array_unspecified_type(message):
    parameter_api = {
        'name': 'name1',
        'schema': {'type': 'array'}}
    value = ['@action1', 2, {'a': 'v', 'b': 6}]
    expected = ['@action1', 2, {'a': 'v', 'b': 6}]
    converted = convert_json(parameter_api, value, message)
    assert converted == expected