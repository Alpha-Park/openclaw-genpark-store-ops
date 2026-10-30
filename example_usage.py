# -*- coding: utf-8 -*-
from client import OpenClawGenParkStoreOps

ops = OpenClawGenParkStoreOps()

# 1. Stochastic EOQ & ROP
inv = ops.calculate_stochastic_eoq_and_rop(annual_demand=12000.0, order_cost_usd=50.0, holding_cost_per_unit_year=4.0, lead_time_days=10.0, demand_daily_std_dev=8.0)
print(f"Inventory Optimization: EOQ={inv['optimal_order_quantity_eoq']} units, Safety Stock={inv['safety_stock_units']}, ROP={inv['reorder_point_rop']}")

# 2. Dynamic Price Elasticity
pricing = ops.optimize_price_elasticity_yield(unit_cost=20.0, base_price=35.0, base_demand=500.0, price_elasticity=2.0)
print(f"\nPrice Yield Optimization: Optimal Price=${pricing['optimal_price_usd']} (Profit Lift: +{pricing['profit_lift_percentage']}%)")

# 3. Stockout Hazard Audit
hazard = ops.audit_stockout_hazard(current_inventory=140, daily_run_rate=20.0, supplier_lead_time_days=10.0)
print(f"\nStockout Audit: {hazard['days_of_inventory_remaining']} days remaining ({hazard['hazard_level']}) -> {hazard['operational_recommendation']}")
