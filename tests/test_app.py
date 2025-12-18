from http import HTTPStatus

from fast_zero.schemas import UserPublic


def test_root_deve_retornar_hello_world(client):
    response = client.get('/')

    assert response.json() == {'message': 'Olá mundo!'}
    assert response.status_code == HTTPStatus.OK


def test_create_user(client):
    response = client.post(
        '/users/',
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': '123456tralala',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'bob',
        'email': 'bob@example.com',
    }


def test_create_user_should_return_409_username_already_exists(client, user):
    response = client.post(
        '/users/',
        json={
            'username': user.username,
            'email': 'bob2@example.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username already exists'}


def test_create_user_should_return_409_email_already_exists(client, user):
    response = client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': user.email,
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email already in use'}


def test_read_users(client, user, token):
    response = client.get(
        '/users/', headers={'Authorization': f'Bearer {token}'}
    )

    user_schema = UserPublic.model_validate(user).model_dump()

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_update_user(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'bob',
        'email': 'bob@example.com',
        'id': 1,
    }


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


def test_update_integrity_error(client, user, token):
    client.post(
        '/users/',
        json={
            'username': 'fausto',
            'email': 'fausto@example.com',
            'password': 'secret',
        },
    )

    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'fausto',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or email already exists'}


def test_read_user_by_id(client, user):
    response = client.get(f'/users/{user.id}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': user.username,
        'email': user.email,
        'id': user.id,
    }


def test_get_read_by_id_return_not_found(client):
    response = client.get('/users/500')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_get_token(client, user):
    response = client.post(
        '/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'acess_token' in token
    assert token['token_type'] == 'Bearer'
