
import rsa

def generate_keys():
    pub, priv = rsa.newkeys(2048)
    return pub.save_pkcs1(), priv.save_pkcs1()

def sign_bytes(private_key_pem: bytes, data: bytes) -> bytes:
    priv = rsa.PrivateKey.load_pkcs1(private_key_pem)
    return rsa.sign(data, priv, 'SHA-256')

def verify_signature(public_key_pem: bytes, data: bytes, signature: bytes) -> bool:
    pub = rsa.PublicKey.load_pkcs1(public_key_pem)
    try:
        rsa.verify(data, signature, pub)
        return True
    except rsa.VerificationError:
        return False
