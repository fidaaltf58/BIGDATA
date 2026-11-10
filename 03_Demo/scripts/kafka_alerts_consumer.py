"""
Consommateur Kafka "métier" (exécuté depuis Windows) :
lit le topic hotel-bookings en temps réel et lève une alerte
pour les réservations à fort risque d'annulation.

  pip install kafka-python-ng
  python kafka_alerts_consumer.py
"""
import csv
from kafka import KafkaConsumer

COLS = ("hotel,is_canceled,lead_time,arrival_date_year,arrival_date_month,arrival_date_week_number,"
        "arrival_date_day_of_month,stays_in_weekend_nights,stays_in_week_nights,adults,children,babies,meal,"
        "country,market_segment,distribution_channel,is_repeated_guest,previous_cancellations,"
        "previous_bookings_not_canceled,reserved_room_type,assigned_room_type,booking_changes,deposit_type,"
        "agent,company,days_in_waiting_list,customer_type,adr,required_car_parking_spaces,"
        "total_of_special_requests,reservation_status,reservation_status_date").split(",")


def risk_score(b: dict) -> int:
    """Règles simples issues de l'analyse exploratoire du dataset."""
    score = 0
    if int(b["lead_time"]) > 120:
        score += 2                      # réservation très anticipée
    if b["deposit_type"] == "Non Refund":
        score += 2                      # paradoxalement très annulée dans ce dataset
    if int(b["previous_cancellations"]) > 0:
        score += 2
    if b["market_segment"] == "Groups":
        score += 1
    if int(b["total_of_special_requests"]) == 0:
        score += 1
    if b["is_repeated_guest"] == "1":
        score -= 2                      # client fidèle
    return score


def main() -> None:
    consumer = KafkaConsumer(
        "hotel-bookings",
        bootstrap_servers="localhost:29092",
        group_id="alertes-annulation",
        auto_offset_reset="earliest",
        value_deserializer=lambda v: v.decode("utf-8"),
    )
    total = alerts = revenue = 0
    print("En écoute sur hotel-bookings ... (Ctrl+C pour arrêter)")
    for msg in consumer:
        row = next(csv.reader([msg.value]))
        if len(row) != len(COLS):
            continue
        b = dict(zip(COLS, row))
        total += 1
        nights = int(b["stays_in_weekend_nights"]) + int(b["stays_in_week_nights"])
        revenue += float(b["adr"]) * nights
        s = risk_score(b)
        if s >= 4:
            alerts += 1
            print(f"⚠ ALERTE risque={s} | {b['hotel']:<12} | {b['country']:<4} | lead={b['lead_time']:>3}j "
                  f"| dépôt={b['deposit_type']:<10} | ADR={b['adr']}€  (partition {msg.partition}, offset {msg.offset})")
        if total % 50 == 0:
            print(f"--- {total} réservations reçues | {alerts} alertes ({alerts / total:.0%}) "
                  f"| CA potentiel cumulé {revenue:,.0f} € ---")


if __name__ == "__main__":
    main()
