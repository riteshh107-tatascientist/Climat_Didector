import os, sys, time, unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.core.security import (
    hash_password, verify_password, create_access_token, decode_access_token, TokenError
)


class TestPasswordHashing(unittest.TestCase):
    def test_hash_is_not_plaintext(self):
        h = hash_password("mypassword123")
        self.assertNotEqual(h, "mypassword123")
        self.assertTrue(h.startswith("pbkdf2_sha256$"))

    def test_verify_correct_password(self):
        h = hash_password("mypassword123")
        self.assertTrue(verify_password("mypassword123", h))

    def test_verify_wrong_password(self):
        h = hash_password("mypassword123")
        self.assertFalse(verify_password("wrongpassword", h))

    def test_same_password_different_hashes(self):
        # Random salt per call -> hashes must differ even for identical input
        h1 = hash_password("samepassword")
        h2 = hash_password("samepassword")
        self.assertNotEqual(h1, h2)
        self.assertTrue(verify_password("samepassword", h1))
        self.assertTrue(verify_password("samepassword", h2))

    def test_verify_rejects_malformed_hash(self):
        self.assertFalse(verify_password("anything", "not-a-real-hash"))


class TestJWT(unittest.TestCase):
    def test_create_and_decode_round_trip(self):
        token = create_access_token(subject="42", extra_claims={"role": "analyst"})
        payload = decode_access_token(token)
        self.assertEqual(payload["sub"], "42")
        self.assertEqual(payload["role"], "analyst")

    def test_invalid_token_raises(self):
        with self.assertRaises(TokenError):
            decode_access_token("not.a.valid.jwt")

    def test_expired_token_raises(self):
        token = create_access_token(subject="1", expires_minutes=-1)  # already expired
        with self.assertRaises(TokenError):
            decode_access_token(token)


if __name__ == "__main__":
    unittest.main()
