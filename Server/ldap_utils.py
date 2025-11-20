from ldap3 import Server, Connection, NTLM, ALL
import os
from dotenv import load_dotenv
load_dotenv()
DOMAIN_CONTROLLER = os.environ.get("DOMAIN_CONTROLLER")

if not DOMAIN_CONTROLLER:
    raise ValueError("DOMAIN_CONTROLLER is not set. Please configure environment variable.")

SERVICE_USER = os.environ.get('DCUSERNAME')
SERVICE_PASS = os.environ.get('DCPASSWORD')
LDAP_GROUP_DN = os.environ.get('LDAP_GROUP_DN',
                               "CN=Allow-Monitor,OU=CA_Office_Users,DC=ad,DC=uskoinc,DC=com")



def user_dn(username):
    """
    Convert 'jdoe' into full DN using service account.
    Returns None if user not found.
    """
    server = Server(DOMAIN_CONTROLLER, get_info=ALL)

    try:
        conn = Connection(
            server,
            user=SERVICE_USER,
            password=SERVICE_PASS,
            authentication=NTLM,
            auto_bind=True
        )
        conn.search(
            search_base="DC=ad,DC=uskoinc,DC=com",
            search_filter=f"(sAMAccountName={username})",
            attributes=["distinguishedName"]
        )
        if conn.entries:
            return conn.entries[0].distinguishedName.value
    except Exception as e:
        print("DN lookup failed:", e)
    return None


def ldap_auth(username, password):
    """
    Check if user credentials are valid.
    Returns True/False.
    """
    server = Server(DOMAIN_CONTROLLER)
    user_ntlm = f"ad\\{username}"  # prepend domain for NTLM

    try:
        conn = Connection(
            server,
            user=user_ntlm,
            password=password,
            authentication=NTLM
        )
        return conn.bind()
    except Exception:
        return False


def is_user_in_group(username):
    """
    Check if the given username is a member of LDAP_GROUP_DN.
    Returns True/False.
    """
    dn = user_dn(username)
    if not dn:
        print("❌ No DN found for user", username)
        return False

    server = Server(DOMAIN_CONTROLLER, get_info=ALL)
    try:
        conn = Connection(
            server,
            user=SERVICE_USER,
            password=SERVICE_PASS,
            authentication=NTLM,
            auto_bind=True
        )
        conn.search(
            search_base=LDAP_GROUP_DN,
            search_filter=f"(member={dn})",
            attributes=["cn"]
        )
        return len(conn.entries) > 0
    except Exception as e:
        print("Group lookup failed:", e)
        return False
