"""Example usage for AgenticDelegatedEscrowSettlementLedger."""
import json
from client import AgenticDelegatedEscrowSettlementLedger

def main():
    print("=== Cryptographic Delegated Agentic Commerce Escrow Ledger Demo ===")
    ledger = AgenticDelegatedEscrowSettlementLedger(platform_fee_bps=150) # 1.5%

    # 1. Lock $450 in conditional escrow (Meta Muse shopping on Shopify merchant)
    print("\n--- 1. Creating Conditional Escrow with Multi-Party Split ---")
    esc = ledger.create_conditional_escrow(
        payer_id="user_alice_wa_01",
        merchant_id="merchant_tokyo_crafts",
        agent_id="consumer_copilot_muse",
        gross_amount_usd=450.0,
        agent_referral_bps=300 # 3.0% agent referral
    )
    print(f"Escrow ID: {esc['escrow_id']}, Status: {esc['status']}")
    print("Payout Split Allocation:")
    print(json.dumps(esc["split_distribution"], indent=2))

    # 2. Carrier delivers package -> release escrow
    print("\n--- 2. Autonomous Proof-of-Delivery Verification & Release ---")
    release = ledger.release_escrow_settlement(
        escrow_id=esc["escrow_id"],
        proof_of_delivery_token="FEDEX-DELIVERED-HASH-883921"
    )
    print(json.dumps(release, indent=2))

    # 3. Audit trail
    print("\n--- 3. Immutable Ledger Event Audit Blocks ---")
    audit = ledger.get_ledger_audit_trail()
    print(f"Total Blocks Recorded: {audit['total_ledger_events']}")
    for b in audit["recent_blocks"]:
        print(f"Block #{b['block_index']}: {b['action']} (Hash: {b['hash'][:18]}...)")

if __name__ == "__main__":
    main()
