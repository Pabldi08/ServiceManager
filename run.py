from app.remote import runRemoteSystemctl

def main():
    result = runRemoteSystemctl(
        hostName="raspberry",
        action="is-active",
        serviceName="gallinerito.service"
    )

    print("Código de salida:", result["returncode"])
    print("Salida:", result["stdout"])
    print("Error:", result["stderr"])

if __name__ == "__main__":
    main()