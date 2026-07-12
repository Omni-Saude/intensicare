"""Test script for verifying fixes."""
import sys, os
sys.path.insert(0, 'src')
os.environ['PYTHONPATH'] = 'src'

import httpx
import base64
import json

BASE = "http://localhost:8000"

async def main():
    async with httpx.AsyncClient() as client:
        # 1. Test JWT claims
        print("=== Fix 1: JWT Claims ===")
        resp = await client.post(f"{BASE}/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        print(f"Login status: {resp.status_code}")
        data = resp.json()
        
        token = data.get("access_token", "")
        if token:
            parts = token.split('.')
            payload = parts[1]
            payload += '=' * (4 - len(payload) % 4)
            decoded = json.loads(base64.urlsafe_b64decode(payload))
            has_is_admin = "is_admin" in decoded
            has_role = "role" in decoded
            print(f"  JWT has 'is_admin': {has_is_admin} (value: {decoded.get('is_admin')})")
            print(f"  JWT has 'role': {has_role} (value: {decoded.get('role')})")
            print(f"  {'✅' if has_is_admin and has_role else '❌'} JWT fix")
        else:
            print(f"  Login response: {data}")
            return
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Test prophylaxis bundles without mpi_id
        print("\n=== Fix 2: Prophylaxis bundles (no mpi_id) ===")
        resp = await client.get(f"{BASE}/api/v1/prophylaxis/bundles", headers=headers)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            bundles_data = resp.json()
            print(f"  ✅ Returns 200 — {len(bundles_data.get('bundles', []))} bundles")
        elif resp.status_code == 422:
            print(f"  ❌ Still 422: {resp.text[:300]}")
        else:
            print(f"  Response ({resp.status_code}): {resp.text[:300]}")
        
        # 3. Test prescriptions state-machine
        print("\n=== Fix 3: Prescriptions state-machine ===")
        resp = await client.get(f"{BASE}/api/v1/prescriptions/state-machine", headers=headers)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"  ✅ Returns 200 (literal route matched correctly)")
        elif resp.status_code == 422:
            print(f"  ❌ Still 422: {resp.text[:300]}")
        else:
            print(f"  Response ({resp.status_code}): {resp.text[:200]}")
        
        # 4. Test vitals without recorded_at
        print("\n=== Fix 4: Vitals without recorded_at ===")
        resp = await client.post(f"{BASE}/api/v1/vitals", headers=headers, json={
            "mpi_id": "TEST-MPI-001",
            "heart_rate": 72,
            "systolic_bp": 120
        })
        print(f"Status: {resp.status_code}")
        if resp.status_code in [200, 201]:
            print(f"  ✅ Vitals accepted without recorded_at")
        elif resp.status_code == 422:
            print(f"  ❌ Still 422: {resp.text[:300]}")
        else:
            print(f"  Response ({resp.status_code}): {resp.text[:200]}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
