# Data Dictionary

## Analytical fact table: `order_fact`

| Field | Type | Definition | Business use |
|---|---|---|---|
| `order_id` | string | Unique order identifier | Order-level grain |
| `order_status` | string | Lifecycle state from the source order table | Delivery funnel |
| `order_purchase_timestamp` | datetime | Customer purchase time | Time-series and seasonality |
| `order_delivered_customer_date` | datetime | Observed customer delivery timestamp | Actual delivery duration |
| `order_estimated_delivery_date` | datetime | Promised/estimated delivery date | Promise variance |
| `product_value` | numeric | Sum of item prices | Merchandise value |
| `freight_value` | numeric | Sum of item freight charges | Shipping value |
| `order_value` | numeric | Product value plus freight value | Exposure and scenario sizing |
| `item_count` | integer | Number of order items | Basket size |
| `seller_count` | integer | Distinct sellers contributing items | Fulfillment complexity proxy |
| `category` | string | English product category; missing mapped to `Other` | Category benchmarking |
| `customer_city` / `customer_state` | string | Customer destination geography | Market performance |
| `seller_city` / `seller_state` | string | Seller origin geography | Seller operations |
| `delivery_days` | numeric | Days from purchase to observed customer delivery | Speed KPI |
| `promised_days` | numeric | Days from purchase to estimated delivery date | Promise KPI |
| `late_days` | numeric | Positive days delivered after estimate; otherwise zero | Late-service severity |
| `is_delivered` | boolean | True when source status is `delivered` | Delivered-order denominator |
| `is_late` | boolean | True when delivered after estimate | Late-rate KPI |
| `is_cancelled` | boolean | True when source status is `canceled` | Cancellation KPI |
| `delivery_status` | string | `On time`, `Late`, `Cancelled`, or `In flight / other` | Operational segmentation |
| `review_score` | numeric | Customer review score from 1 to 5; zero means no review | Experience analysis |
| `review_label` | string | `At risk` for 1–2, `Neutral` for 3, `Healthy` for 4–5 | Review-health segmentation |
| `purchase_month` | string | Calendar month derived from purchase timestamp | Trend analysis |
| `purchase_day` | string | Day name derived from purchase timestamp | Day-of-week analysis |
| `purchase_hour` | integer | Hour derived from purchase timestamp | Intraday analysis |
| `weekend_flag` | boolean | True for Saturday or Sunday | Weekend comparison |
| `distance_proxy` | integer | 1 when seller and customer are in different states; null when geography is missing | Directional geography proxy, not kilometres |

## Grain and denominator policy

The fact table has one row per order after item aggregation. Late rate is calculated only on delivered orders when the question is delivery reliability. Cancellation rate uses all filtered orders. Review analysis uses orders with a non-zero review score. Seller and category leaderboards use minimum-volume thresholds to reduce small-sample noise.

## Known limitations

The public source does not contain rider assignment timestamps, route telemetry, weather, traffic, restaurant preparation time or true kilometre distance. These are future data requirements. The dashboard therefore supports **diagnosis and prioritisation**, not causal attribution or a production SLA forecast.
