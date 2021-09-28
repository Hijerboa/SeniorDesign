from flask import jsonify

def make_error(status_code, sub_code, message, action):
    """
    Helper function to make error responses
    :param status_code: HTTP status code to be provided to user
    :param sub_code: Sub code to be used internally for troubleshooting
    :param message: Message to tell user
    :param action: Action to inform user to take
    :return: A jsonified error response
    """
    response = jsonify({
        'status': status_code,
        'sub_code': sub_code,
        'message': message,
        'action': action
    })
    response.status_code = status_code
    return response