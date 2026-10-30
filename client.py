# -*- coding: utf-8 -*-
"""
OpenClaw GenPark Store Ops - Stochastic EOQ Safety Stock & Dynamic Elasticity Yield Optimizer
Standard Library only: math, typing.
Calculates Economic Order Quantity (EOQ), stochastic safety stock buffers, reorder points (ROP),
and derives analytical price-elasticity profit-maximizing optimal pricing.
"""

import math
from typing import Dict, List, Any

class OpenClawGenParkStoreOps:
    def __init__(self, default_service_z: float = 1.645): # 95% service level
        self.default_z = default_service_z

    def calculate_stochastic_eoq_and_rop(self, annual_demand: float,
                                         order_cost_usd: float,
                                         holding_cost_per_unit_year: float,
                                         lead_time_days: float,
                                         demand_daily_std_dev: float,
                                         service_level_z: float = None) -> Dict[str, Any]:
        """
        Calculates classic Economic Order Quantity and stochastic Reorder Point:
        EOQ = sqrt( (2 * D * S) / H )
        Safety Stock SS = Z * sigma_d * sqrt(L)
        ROP = d_daily * L + SS
        """
        z = service_level_z if service_level_z is not None else self.default_z
        D = max(1.0, annual_demand)
        S = max(0.01, order_cost_usd)
        H = max(0.01, holding_cost_per_unit_year)
        L = max(0.1, lead_time_days)

        # 1. Economic Order Quantity
        eoq = math.sqrt((2.0 * D * S) / H)

        # 2. Daily demand and lead time standard deviation
        daily_demand = D / 365.0
        lead_time_std_dev = demand_daily_std_dev * math.sqrt(L)
        safety_stock = z * lead_time_std_dev

        # 3. Reorder Point (ROP)
        rop = (daily_demand * L) + safety_stock

        # Total annual logistics cost
        orders_per_year = D / eoq
        annual_order_cost = orders_per_year * S
        annual_holding_cost = (eoq / 2.0 + safety_stock) * H
        total_cost = annual_order_cost + annual_holding_cost

        return {
            "annual_demand_units": D,
            "optimal_order_quantity_eoq": round(eoq, 1),
            "safety_stock_units": round(safety_stock, 1),
            "reorder_point_rop": round(rop, 1),
            "orders_per_year": round(orders_per_year, 2),
            "annual_ordering_cost_usd": round(annual_order_cost, 2),
            "annual_holding_cost_usd": round(annual_holding_cost, 2),
            "total_annual_inventory_cost_usd": round(total_cost, 2)
        }

    def optimize_price_elasticity_yield(self, unit_cost: float,
                                        base_price: float,
                                        base_demand: float,
                                        price_elasticity: float = 1.5) -> Dict[str, Any]:
        """
        Calculates profit-maximizing optimal price under constant elasticity: Q(p) = Q0 * (p / p0)^(-eps)
        Optimal markup price: p* = c * (eps / (eps - 1)) for eps > 1.0.
        """
        eps = max(1.01, price_elasticity)
        c = max(0.01, unit_cost)

        optimal_price = c * (eps / (eps - 1.0))
        
        # Calculate demand and profit at base vs optimal
        ratio_opt = optimal_price / max(0.01, base_price)
        opt_demand = base_demand * (ratio_opt ** (-eps))
        opt_profit = (optimal_price - c) * opt_demand

        base_profit = (base_price - c) * base_demand
        profit_lift_pct = ((opt_profit - base_profit) / max(0.01, base_profit)) * 100.0 if base_profit > 0 else 0.0

        return {
            "unit_cost_usd": c,
            "base_price_usd": base_price,
            "base_profit_usd": round(base_profit, 2),
            "price_elasticity_epsilon": eps,
            "optimal_price_usd": round(optimal_price, 2),
            "expected_demand_at_optimal": round(opt_demand, 1),
            "expected_profit_at_optimal_usd": round(opt_profit, 2),
            "profit_lift_percentage": round(profit_lift_pct, 2)
        }

    def audit_stockout_hazard(self, current_inventory: int,
                              daily_run_rate: float,
                              supplier_lead_time_days: float) -> Dict[str, Any]:
        """
        Audits stockout hazard based on inventory run rate vs supplier lead time.
        """
        rate = max(0.01, daily_run_rate)
        days_of_inventory = current_inventory / rate
        coverage_ratio = days_of_inventory / max(0.1, supplier_lead_time_days)

        if coverage_ratio < 1.0:
            hazard = "CRITICAL_STOCKOUT_IMMINENT"
            urgency = "TRIGGER_EMERGENCY_EXPEDITED_ORDER"
        elif coverage_ratio < 1.5:
            hazard = "ELEVATED_INVENTORY_DEPLETION_RISK"
            urgency = "DISPATCH_STANDARD_REORDER"
        else:
            hazard = "HEALTHY_INVENTORY_COVERAGE"
            urgency = "NOMINAL_MONITORING"

        return {
            "current_inventory": current_inventory,
            "days_of_inventory_remaining": round(days_of_inventory, 1),
            "lead_time_days": supplier_lead_time_days,
            "lead_time_coverage_ratio": round(coverage_ratio, 2),
            "hazard_level": hazard,
            "operational_recommendation": urgency
        }
