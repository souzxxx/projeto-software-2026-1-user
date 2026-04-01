def test_get_user_404(client):
    get_response = client.get("/users/1")
    assert get_response.status_code == 404


def test_create_and_get_user_and_delete_user(client):
    # Criar usuário
    create_response = client.post("/users", json={"name": "teste", "email": "teste@example.com"})
    assert create_response.status_code == 201
    data = create_response.get_json()
    user_id = data["id"]
    assert data["name"] == "teste"
    assert data["email"] == "teste@example.com"

    # Recuperar usuário
    get_response = client.get(f"/users/{user_id}")
    assert get_response.status_code == 200
    get_data = get_response.get_json()
    assert get_data["id"] == user_id
    assert get_data["name"] == "teste"
    assert get_data["email"] == "teste@example.com"

    # Deletar usuário
    delete_response = client.delete(f"/users/{user_id}")
    assert delete_response.status_code == 204

    # Confirmar que foi deletado
    get_after_delete = client.get(f"/users/{user_id}")
    assert get_after_delete.status_code == 404


def test_create_and_delete_user(client):
    # Criar usuário
    create_response = client.post("/users", json={"name": "teste1", "email": "teste1@example.com"})
    assert create_response.status_code == 201
    data = create_response.get_json()
    user_id = data["id"]

    # Deletar usuário
    delete_response = client.delete(f"/users/{user_id}")
    assert delete_response.status_code == 204


def test_create_two_users_and_list_and_delete_both_users(client):
    # Criar dois usuários
    r1 = client.post("/users", json={"name": "teste2", "email": "teste2@example.com"})
    r2 = client.post("/users", json={"name": "teste3", "email": "teste3@example.com"})
    assert r1.status_code == 201
    assert r2.status_code == 201
    id1 = r1.get_json()["id"]
    id2 = r2.get_json()["id"]

    # Listar usuários
    list_response = client.get("/users")
    assert list_response.status_code == 200
    users = list_response.get_json()
    ids = [u["id"] for u in users]
    assert id1 in ids
    assert id2 in ids

    # Deletar ambos
    assert client.delete(f"/users/{id1}").status_code == 204
    assert client.delete(f"/users/{id2}").status_code == 204
