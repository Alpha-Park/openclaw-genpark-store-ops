# -*- coding: utf-8 -*-
import sys, json
from client import OpenClawGenParkStoreOps

client = OpenClawGenParkStoreOps()

TOOLS = [
    {
        "name": "calculate_stochastic_eoq_and_rop",
        "description": "Calculates EOQ, stochastic safety stock buffers, and reorder point (ROP).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "annual_demand": {"type": "number"},
                "order_cost_usd": {"type": "number"},
                "holding_cost_per_unit_year": {"type": "number"},
                "lead_time_days": {"type": "number"},
                "demand_daily_std_dev": {"type": "number"},
                "service_level_z": {"type": "number"}
            },
            "required": ["annual_demand", "order_cost_usd", "holding_cost_per_unit_year", "lead_time_days", "demand_daily_std_dev"]
        }
    },
    {
        "name": "optimize_price_elasticity_yield",
        "description": "Calculates profit-maximizing optimal price under constant price elasticity.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "unit_cost": {"type": "number"},
                "base_price": {"type": "number"},
                "base_demand": {"type": "number"},
                "price_elasticity": {"type": "number"}
            },
            "required": ["unit_cost", "base_price", "base_demand"]
        }
    },
    {
        "name": "audit_stockout_hazard",
        "description": "Audits days of inventory coverage vs supplier lead time to flag stockout hazard.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "current_inventory": {"type": "integer"},
                "daily_run_rate": {"type": "number"},
                "supplier_lead_time_days": {"type": "number"}
            },
            "required": ["current_inventory", "daily_run_rate", "supplier_lead_time_days"]
        }
    }
]

def handle_request(req):
    method = req.get("method")
    rid = req.get("id")
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": rid, "result": {"tools": TOOLS}}
    elif method == "tools/call":
        params = req.get("params", {})
        tname = params.get("name")
        args = params.get("arguments", {})
        if tname == "calculate_stochastic_eoq_and_rop":
            res = client.calculate_stochastic_eoq_and_rop(args["annual_demand"], args["order_cost_usd"], args["holding_cost_per_unit_year"], args["lead_time_days"], args["demand_daily_std_dev"], args.get("service_level_z"))
            return {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}}
        elif tname == "optimize_price_elasticity_yield":
            res = client.optimize_price_elasticity_yield(args["unit_cost"], args["base_price"], args["base_demand"], args.get("price_elasticity", 1.5))
            return {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}}
        elif tname == "audit_stockout_hazard":
            res = client.audit_stockout_hazard(args["current_inventory"], args["daily_run_rate"], args["supplier_lead_time_days"])
            return {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}}
        return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": "Method not found"}}
    return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32600, "message": "Invalid Request"}}

def main():
    for line in sys.stdin:
        if not line.strip(): continue
        try:
            req = json.loads(line)
            resp = handle_request(req)
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}}) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
