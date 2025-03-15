import keyring

# Guardar credenciales de LinkedIn
keyring.set_password("linkedin", "email", "linkedin@email.com")
keyring.set_password("linkedin", "password", "linkedin_password")

print("✅ Credenciales almacenadas de forma segura.")
