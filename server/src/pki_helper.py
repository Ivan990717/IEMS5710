from getpass import getpass

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from datetime import datetime, timedelta
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes


def generate_private_key(filename: str, passphrase: str):
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )

    utf8_pass = passphrase.encode("utf-8")
    algorithm = serialization.BestAvailableEncryption(utf8_pass)

    with open(filename, "wb") as keyfile:
        keyfile.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=algorithm,
            )
        )

    return private_key


def generate_public_key(private_key, filename, **kwargs):
    '''

    :param private_key:
    :param filename:
    :param kwargs:
    :return:

    generate_public_key(
    private_key,
    filename="xx",
    country="US",
    state="Maryland",
    locality="Baltimore",
    org="My CA Company",
    hostname="my-ca.com",
    )
    '''
    subject = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, kwargs["country"]),
            x509.NameAttribute(
                NameOID.STATE_OR_PROVINCE_NAME, kwargs["state"]
            ),
            x509.NameAttribute(NameOID.LOCALITY_NAME, kwargs["locality"]),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, kwargs["org"]),
            x509.NameAttribute(NameOID.COMMON_NAME, kwargs["hostname"]),
        ]
    )

    # Because this is self_signed, the issuer is always the subject
    issuer = subject

    # This certificate is valid from now until 30 days
    valid_from = datetime.utcnow()
    valid_to = valid_from + timedelta(days=30)

    # Used to build the certificate
    builder = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(valid_from)
        .not_valid_after(valid_to)
    )

    # Sign the certificate with the private key
    public_key = builder.sign(
        private_key, hashes.SHA256(), default_backend()
    )

    with open(filename, "wb") as certfile:
        certfile.write(public_key.public_bytes(serialization.Encoding.PEM))

    return public_key

def generate_csr(private_key, filename, **kwargs):
    subject = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, kwargs["country"]),
            x509.NameAttribute(
                NameOID.STATE_OR_PROVINCE_NAME, kwargs["state"]
            ),
            x509.NameAttribute(NameOID.LOCALITY_NAME, kwargs["locality"]),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, kwargs["org"]),
            x509.NameAttribute(NameOID.COMMON_NAME, kwargs["hostname"]),
        ]
    )

    # Generate any alternative dns names
    alt_names = []
    for name in kwargs.get("alt_names", []):
        alt_names.append(x509.DNSName(name))
    san = x509.SubjectAlternativeName(alt_names)

    builder = (
        x509.CertificateSigningRequestBuilder()
        .subject_name(subject)
        .add_extension(san, critical=False)
    )

    csr = builder.sign(private_key, hashes.SHA256(), default_backend())
    with open(filename, "wb") as csrfile:
        csrfile.write(csr.public_bytes(serialization.Encoding.PEM))

    return csr

# private_key = generate_private_key("../../test/ca-private-key.pem", "regina")
# print(private_key)

# key = generate_public_key(
#     private_key = private_key,
#     filename="../../test/ca-public-key.pem",
#     country="US",
#     state="Maryland",
#     locality="Baltimore",
#     org="My CA Company",
#     hostname="my-ca.com",
#     )
# print(key)
#
# server_private_key = generate_private_key("../../test/server-private-key.pem", "regina")
# print(server_private_key)
# #
# generate_csr(
#     server_private_key,
#     filename="../../test/server-csr.pem",
#     country="US",
#     state="Maryland",
#     locality="Baltimore",
#     org="My Company",
#     alt_names=["localhost"],
#     hostname="my-site.com")
#
def sign_csr(csr, ca_public_key, ca_private_key, new_filename):
    valid_from = datetime.utcnow()
    valid_until = valid_from + timedelta(days=30)

    builder = (
        x509.CertificateBuilder()
        .subject_name(csr.subject)
        .issuer_name(ca_public_key.subject)
        .public_key(csr.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(valid_from)
        .not_valid_after(valid_until)
    )

    for extension in csr.extensions:
        builder = builder.add_extension(extension.value, extension.critical)

    public_key = builder.sign(
        private_key=ca_private_key,
        algorithm=hashes.SHA256(),
        backend=default_backend(),
    )

    with open(new_filename, "wb") as keyfile:
        keyfile.write(public_key.public_bytes(serialization.Encoding.PEM))

# csr_file = open("../../test/server-csr.pem", "rb")
# csr = x509.load_pem_x509_csr(csr_file.read(), default_backend())
# print(csr)
#
# ca_public_key_file = open("../../test/ca-public-key.pem", "rb")
# ca_public_key = x509.load_pem_x509_certificate(
#     ca_public_key_file.read(),
#     default_backend())
# print(ca_public_key)
#
# ca_private_key_file = open("../../test/ca-private-key.pem", "rb")
# ca_private_key = serialization.load_pem_private_key(
#     ca_private_key_file.read(),
#     getpass().encode("utf-8"),
#     default_backend(),)
#
# print(ca_private_key)
#
# sign_csr(csr, ca_public_key, ca_private_key, "../../test/server-public-key.pem")