#!/usr/bin/env python3
"""
Kargadan Cloud Python SDK
Complete API client for kargadan.ir (Cloud VPS, Power Management, Billing, Snapshots, SSH Keys)
Compatible with Linux, macOS, and Docker environments.
"""

import json
import base64
import subprocess
import time
import ssl
import http.cookiejar
import urllib.request
import urllib.parse

ACTION_IDS = {
    # Account & Profile
    "GET_ME": "00ebc0d0b18fa652247eca82cb58cfc282e40a0d1e",
    "NOTIFICATIONS": "40def9537484b3d4bf767c77dd72d4ebcba077d554",
    
    # Virtual Machines / VPS
    "CLOUD_MACHINES": "4015ad04fdca6ef1345bb2440f262c57c5f8f53e1b",
    "CLOUD_MACHINE": "40b8d653f88a301a89c7ef902fbd71c43e511083c2",
    "MACHINE_ACTION": "40629f5e30edfe7a85648165cc82f12ba67454a6af",
    "MACHINE_CREATE": "40b61394de498aceefe59eb349b2bfce06f7047472",
    "MACHINE_DELETE": "400c6f874d96143e3a01e732f79b97b9184d4a2d84",
    "MACHINE_RESIZE": "4045802c6bfb82f63ce532d3a63ededdbd2383437f",
    "MACHINE_RESET_PASSWORD": "40290c6bf4f3a3b5ed10932e35fc79499d606e62d8",
    "MACHINE_REBUILD": "402ff5abcfc1634e83946729b277a3fcf287f7726a",
    "MACHINE_LOGS": "402f4b196ff8db9c13a7d3741928ba8789d885648e",
    "MACHINE_GRAPH": "4031661af8757665aba773bb3c619e550fcb99e238",
    
    # Infrastructure & Templates
    "CLUSTERS": "406d51c17008cd7eadbff8906eedac547d04ed0084",
    "TEMPLATES": "40cd8214ad4ac8752c5a86dd34f185e09fd02555ef",
    "NETWORKS": "407f0752136fe25a71d60e4cbab0db373ba7284789",
    "EXTRA_IP": "409bf193779591b170baf7537904f654b394edad75",
    
    # Backups & Snapshots
    "SNAPSHOT_CREATE": "40941114ca4d50a1dd54b56cdd8f59312352546750",
    "SNAPSHOT_DELETE": "406db8794f69d0a12da099efaf72ea4ec7cebda6ce",
    "SNAPSHOT_RESTORE": "406aedb660293ce061f359ff9ec2ab4f08714f41c3",
    "BACKUP_BUY": "4079d5b009c7148b731b45d7bbfd18c312f2976f4d",
    "BACKUP_DELETE": "40e7526815a2ed73b09dbf98ce663a0b66f5a1a2b3",
    "BACKUP_RESTORE": "407de2db405c6ad67954af107031101392c07d94e0",
    
    # SSH Keys / Certificates
    "CERTIFICATES": "409e2a127cc5d3a84c245c919a41954b54695bfb28",
    "CERTIFICATE_CREATE": "405e18397fa8c182e2dbd64a0bc82b224718dec9ac",
    "CERTIFICATE_DELETE": "401dc7e54eef1d4147284d7bbcd3f01b6fc47e6754",
    
    # Financial & Billing
    "WALLET_CHARGE": "40c19e7616b0699caed120d97549e55bd5d5c568d8",
    "PAYMENT_GET_URL": "40fe4a898955f8d6181c38a19f6e0eb4098b2d5854",
    "INVOICES": "40cba87cb5fdb66301c4026405d3484a824691c49c",
    "INVOICE_PAY_WALLET": "40721aa15ced8c9f5219c8380377664da7df20e2cb",
    "TRANSACTIONS": "401d190d359a9ad38201ce1450d5e8d26cf2c5a67d",
    
    # Tickets
    "TICKETS": "40d858a6444acdbc73bedaa312d6fa91924a033f56",
    "TICKET_DETAIL": "40cfff76e74b1fa808b971ed95bfca6ec030352c70",
    "TICKET_CREATE": "40a45de2c0e17856084a9ec36f942c44a382ce9077",
    "TICKET_MESSAGE": "4041d6efd789265148a5d2c29077c8f2d7ff513379",
    "TICKET_CLOSE": "407261616c8f6fb6bbb0eabdeb928b63375948e839",
    
    # Auth
    "USER_SEND_CODE": "4050db76e9473e24037587108bbe73ef9886880eed",
    "USER_VERIFY_CODE": "40e235827a55c792c65aaf5c09cec38c5e44e52f0d",
}


class KargadanClient:
    """
    Client for interacting with Kargadan Cloud API via Next.js Server Actions.
    Supports in-tab AppleScript execution (reusing live browser cookies) and direct standalone HTTP.
    """
    
    BASE_URL = "https://kargadan.ir"
    
    def __init__(self, mode="auto", session_cookie=None):
        self.session_cookie = session_cookie
        self.cookie_jar = http.cookiejar.CookieJar()
        ctx = ssl._create_unverified_context()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPSHandler(context=ctx),
            urllib.request.HTTPCookieProcessor(self.cookie_jar)
        )
        
        if mode == "auto":
            if self._has_chrome_tab():
                self.mode = "chrome_tab"
            else:
                self.mode = "http"
        else:
            self.mode = mode

    def _has_chrome_tab(self):
        """Check if an open tab exists on macOS Google Chrome."""
        try:
            cmd = "osascript -e 'tell application \"Google Chrome\" to return (count of (tabs of windows whose URL contains \"kargadan.ir\"))'"
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=2)
            return res.stdout.strip() not in ["0", "", "missing value"]
        except Exception:
            return False

    def _run_js_in_tab(self, js_code):
        wrapped = f"(() => {{ try {{ {js_code} }} catch(e) {{ return JSON.stringify({{'__error__': e.toString()}}); }} }})()"
        b64 = base64.b64encode(wrapped.encode('utf-8')).decode('utf-8')
        js_eval = f"window.eval(new TextDecoder().decode(Uint8Array.from(window.atob('{b64}'), c => c.charCodeAt(0))))"
        as_js_eval = js_eval.replace('\\', '\\\\').replace('"', '\\"')
        
        apple_script = f'''
tell application "Google Chrome"
    repeat with w in windows
        repeat with t in tabs of w
            if (URL of t contains "kargadan.ir") then
                return (execute t javascript "{as_js_eval}")
            end if
        end repeat
    end repeat
    return "TAB_NOT_FOUND"
end tell
'''
        res = subprocess.run(['osascript', '-e', apple_script], capture_output=True, text=True)
        return res.stdout.strip()

    def call_action(self, action_id, args=None, endpoint="/dashboard"):
        """Call a Next.js Server Action with JSON payload."""
        if args is None:
            args = []
        elif not isinstance(args, list):
            args = [args]

        if self.mode == "chrome_tab":
            return self._call_action_tab(action_id, args, endpoint)
        else:
            return self._call_action_http(action_id, args, endpoint)

    def _call_action_tab(self, action_id, args, endpoint):
        args_json = json.dumps(args, ensure_ascii=False)
        req_id = f"__req_{int(time.time()*1000)}"

        js_script = f"""
fetch('{endpoint}', {{
    method: 'POST',
    headers: {{
        'Next-Action': '{action_id}',
        'Content-Type': 'application/json',
        'Accept': 'text/x-component'
    }},
    body: JSON.stringify({args_json})
}})
.then(r => r.text())
.then(t => {{ window.{req_id} = t; }})
.catch(e => {{ window.{req_id} = 'ERROR:' + e.toString(); }});
return 'TRIGGERED';
"""
        self._run_js_in_tab(js_script)
        
        for _ in range(20):
            time.sleep(0.3)
            check_js = f"return window.{req_id} || '';"
            val = self._run_js_in_tab(check_js)
            if val and val != "missing value":
                self._run_js_in_tab(f"delete window.{req_id};")
                return self._parse_rsc_response(val)
                
        raise TimeoutError(f"Action {action_id} timed out waiting for tab response.")

    def _call_action_http(self, action_id, args, endpoint):
        url = f"{self.BASE_URL}{endpoint}"
        body_bytes = json.dumps(args, ensure_ascii=False).encode('utf-8')
        
        req = urllib.request.Request(
            url,
            data=body_bytes,
            headers={
                "Next-Action": action_id,
                "Content-Type": "application/json",
                "Accept": "text/x-component",
                "User-Agent": "Mozilla/5.0 (KargadanCloudClient/1.0)",
            }
        )
        if self.session_cookie:
            req.add_header("Cookie", self.session_cookie)
            
        with self.opener.open(req) as resp:
            text = resp.read().decode('utf-8')
            return self._parse_rsc_response(text)

    def _parse_rsc_response(self, text):
        """Parse React Server Components (RSC) stream format."""
        lines = text.strip().split('\n')
        parsed = {}
        for line in lines:
            if ':' in line:
                idx, payload = line.split(':', 1)
                try:
                    data = json.loads(payload)
                    parsed[idx] = data
                except Exception:
                    parsed[idx] = payload
                    
        if "1" in parsed and isinstance(parsed["1"], dict):
            return parsed["1"]
        return parsed

    # --- Standalone Auth Methods ---

    def get_csrf_token(self):
        """Fetch fresh CSRF token from Auth.js."""
        req = urllib.request.Request(f"{self.BASE_URL}/api/auth/csrf")
        with self.opener.open(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return data.get("csrfToken")

    def login_with_password(self, username, password):
        """Authenticate using username/email and password."""
        csrf = self.get_csrf_token()
        payload = urllib.parse.urlencode({
            "username": username,
            "password": password,
            "csrfToken": csrf,
            "callbackUrl": f"{self.BASE_URL}/dashboard"
        }).encode('utf-8')
        
        req = urllib.request.Request(
            f"{self.BASE_URL}/api/auth/callback/password",
            data=payload,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Auth-Return-Redirect": "1"
            }
        )
        with self.opener.open(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data.get("url") and "error=" not in data.get("url"):
                return True
            raise ValueError(f"Login failed: {data}")

    def request_otp(self, cellphone):
        """Request 5-digit verification code sent via SMS."""
        return self.call_action(
            ACTION_IDS["USER_SEND_CODE"],
            {"cellphone": cellphone},
            endpoint="/auth/login/otp"
        )

    def verify_otp(self, cellphone, code):
        """Verify 5-digit OTP code and establish authenticated session."""
        csrf = self.get_csrf_token()
        payload = urllib.parse.urlencode({
            "cellphone": cellphone,
            "code": str(code),
            "referrer_code": "",
            "csrfToken": csrf,
            "callbackUrl": f"{self.BASE_URL}/dashboard"
        }).encode('utf-8')
        
        req = urllib.request.Request(
            f"{self.BASE_URL}/api/auth/callback/otp",
            data=payload,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Auth-Return-Redirect": "1"
            }
        )
        with self.opener.open(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data.get("url") and "error=" not in data.get("url"):
                return True
            raise ValueError(f"OTP verification failed: {data}")

    # --- High-Level Cloud Methods ---

    def get_me(self):
        """Fetch current user profile, balance, and club status."""
        return self.call_action(ACTION_IDS["GET_ME"], [])

    def list_machines(self, page=1, limit=50):
        """List all virtual servers/machines in the account."""
        res = self.call_action(
            ACTION_IDS["CLOUD_MACHINES"],
            {"page": page, "limit": limit, "sort_by": "DESC", "sort_field": "ID"}
        )
        if isinstance(res, dict) and "CloudMachinesClient" in res:
            return res["CloudMachinesClient"].get("data", [])
        return res

    def get_machine(self, machine_id):
        """Get full details of a specific virtual machine."""
        res = self.call_action(
            ACTION_IDS["CLOUD_MACHINE"],
            {"id": machine_id},
            endpoint=f"/dashboard/machines/{machine_id}"
        )
        if isinstance(res, dict) and "CloudMachineClient" in res:
            return res["CloudMachineClient"]
        return res

    def machine_action(self, machine_id, action_name):
        """
        Execute power management on a machine.
        Valid action_name values:
        - RESUME: Power on / start
        - POWEROFF: Graceful shutdown
        - POWEROFF_HARD: Force power off
        - REBOOT: Graceful reboot
        - REBOOT_HARD: Force hardware reboot
        """
        valid_actions = ["RESUME", "POWEROFF", "POWEROFF_HARD", "REBOOT", "REBOOT_HARD"]
        if action_name.upper() not in valid_actions:
            raise ValueError(f"Invalid action: {action_name}. Must be one of {valid_actions}")
            
        return self.call_action(
            ACTION_IDS["MACHINE_ACTION"],
            {"machine_id": machine_id, "action_name": action_name.upper()},
            endpoint=f"/dashboard/machines/{machine_id}"
        )

    def delete_machine(self, machine_id):
        """Delete / terminate a virtual machine."""
        return self.call_action(
            ACTION_IDS["MACHINE_DELETE"],
            {"id": machine_id},
            endpoint=f"/dashboard/machines/{machine_id}"
        )

    def reset_machine_password(self, machine_id):
        """Reset root password for a machine."""
        return self.call_action(
            ACTION_IDS["MACHINE_RESET_PASSWORD"],
            {"id": machine_id},
            endpoint=f"/dashboard/machines/{machine_id}"
        )

    def resize_machine(self, machine_id, cpu, memory_gb, disk_gb):
        """Resize CPU, RAM, or Disk for a machine."""
        return self.call_action(
            ACTION_IDS["MACHINE_RESIZE"],
            {"machine_id": machine_id, "cpu": cpu, "memory": memory_gb, "disk": disk_gb},
            endpoint=f"/dashboard/machines/{machine_id}"
        )

    def create_machine(self, title, cluster_id, template_id, cpu, memory_gb, disk_gb, password=None, certificate_id=None):
        """Create a new Cloud VPS instance."""
        payload = {
            "title": title,
            "cluster_id": cluster_id,
            "template_id": template_id,
            "cpu": cpu,
            "memory": memory_gb,
            "disk": disk_gb,
        }
        if certificate_id:
            payload["certificate_id"] = certificate_id
        if password:
            payload["password"] = password
            
        return self.call_action(
            ACTION_IDS["MACHINE_CREATE"],
            payload,
            endpoint="/dashboard/machines/create"
        )

    def list_invoices(self, page=1, limit=50):
        """List billing invoices."""
        return self.call_action(
            ACTION_IDS["INVOICES"],
            {"page": page, "limit": limit}
        )

    def list_transactions(self, page=1, limit=50):
        """List financial transactions and deposits."""
        return self.call_action(
            ACTION_IDS["TRANSACTIONS"],
            {"page": page, "limit": limit}
        )

    def list_tickets(self, page=1, limit=50):
        """List support tickets."""
        return self.call_action(
            ACTION_IDS["TICKETS"],
            {"page": page, "limit": limit}
        )
