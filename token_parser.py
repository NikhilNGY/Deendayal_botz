class TokenParser:
    def __init__(self, token: str):
        # Store the raw token string
        self.token = token

    def get(self) -> str:
        """
        Return the raw token.
        """
        return self.token

    def split(self, sep=":"):
        """
        Split the token by separator (default ':').
        Useful if token has multiple parts like 'id:secret'.
        """
        return self.token.split(sep)

    def __str__(self):
        return self.token
