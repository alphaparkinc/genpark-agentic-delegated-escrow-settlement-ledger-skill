"""MCP Server for Agentic Delegated Escrow Settlement Ledger."""
import sys
import json
import time
from client import AgenticDelegatedEscrowSettlementLedger

ledger = AgenticDelegatedEscrowSettlementLedger()

def handle_call_tool(params):
    name = params.get("name")
    args = params.get("arguments", {})
    if name != "manage_agentic_escrow_ledger":
        raise ValueError(f"Unknown tool: {name}")

    action = args.get("action", "get_ledger_audit_trail")
    if action == "create_conditional_escrow":
        return ledger.create_conditional_escrow(
            payer_id=args.get("payer_id", "user_1"),
            merchant_id=args.get("merchant_id", "merchant_shopify_1"),
            agent_id=args.get("agent_id", "muse_agent_007"),
            gross_amount_usd=float(args.get("gross_amount_usd", 100.0)),
            agent_referral_bps=int(args.get("agent_referral_basis_points", 300))
        )
    elif action == "release_escrow_settlement":
        return ledger.release_escrow_settlement(
            escrow_id=args.get("escrow_id"),
            proof_of_delivery_token=args.get("proof_of_delivery_token", "POD-TRACK-9912")
        )
    elif action == "freeze_disputed_escrow":
        return ledger.freeze_disputed_escrow(
            escrow_id=args.get("escrow_id"),
            dispute_reason=args.get("dispute_reason", "Goods not delivered")
        )
    elif action == "get_ledger_audit_trail":
        return ledger.get_ledger_audit_trail()
    else:
        raise ValueError(f"Invalid action: {action}")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Running self-test...")
        esc = ledger.create_conditional_escrow("buyer_1", "seller_2", "agent_3", 250.0)
        assert esc["status"] == "LOCKED_IN_ESCROW"
        rel = ledger.release_escrow_settlement(esc["escrow_id"], "DELIVERY-OK")
        assert rel["status"] == "SETTLED_RELEASED"
        print("Self-test PASSED!")
        sys.exit(0)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            msg_id = req.get("id")
            method = req.get("method")
            if method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "serverInfo": {"name": "AgenticDelegatedEscrowSettlementLedger", "version": "1.0.0"},
                        "capabilities": {"tools": {}}
                    }
                }
            elif method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "tools": [{
                            "name": "manage_agentic_escrow_ledger",
                            "description": "Agentic escrow and multi-party settlement: lock funds conditionally, release upon delivery proof, execute fee splits, and freeze contested transactions.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "action": {"type": "string", "enum": ["create_conditional_escrow", "release_escrow_settlement", "freeze_disputed_escrow", "get_ledger_audit_trail"]},
                                    "escrow_id": {"type": "string"},
                                    "payer_id": {"type": "string"},
                                    "merchant_id": {"type": "string"},
                                    "agent_id": {"type": "string"},
                                    "gross_amount_usd": {"type": "number"},
                                    "agent_referral_basis_points": {"type": "integer"},
                                    "proof_of_delivery_token": {"type": "string"},
                                    "dispute_reason": {"type": "string"}
                                },
                                "required": ["action"]
                            }
                        }]
                    }
                }
            elif method == "tools/call":
                res = handle_call_tool(req.get("params", {}))
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
                }
            else:
                resp = {"jsonrpc": "2.0", "id": msg_id, "result": {}}
            print(json.dumps(resp), flush=True)
        except Exception as e:
            err_resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32000, "message": str(e)}}
            print(json.dumps(err_resp), flush=True)

if __name__ == "__main__":
    main()
