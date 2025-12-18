import psycopg
import datetime
import smtplib
import time
from email.message import EmailMessage
import traceback

# PostgreSQL bağlantısı
conn_info = "host=127.0.0.1 port=5432 dbname=scada user=postgres password=sCd06"
log_file = r"E:\Scada\Logs\cleanup_test.log"

# E-posta gönderim fonksiyonu
def send_email(subject, body):
    msg = EmailMessage()
    msg['From'] = 'Scada@europowersolar.com'
    msg['To'] = ', '.join([
        'ege.telli@europowerenerji.com.tr',
        'zeki.arslan@europowerenerji.com.tr',
        'berat.karacaoglu@europowerenerji.com.tr',
        'batuhan.tumer@europowerenerji.com.tr',
        'sefer.gultekin@europowerenerji.com.tr',
    ])
    msg['Subject'] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP('mail.europowersolar.com', 587) as smtp:
            smtp.login('Scada@europowersolar.com', 'es0606')
            smtp.send_message(msg)
    except Exception as e:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now()}] Mail gönderilemedi: {e}\n")

# Temizlik işlemini tablo bazlı yapan fonksiyon
def run_cleanup_for_table(table_name, params):
    start_time = datetime.datetime.now()
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{start_time}] Cleanup started for {table_name}.\n")

    try:
        with psycopg.connect(conn_info) as conn:
            with conn.cursor() as cur:
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(f"[{datetime.datetime.now()}] Deleting duplicates query started for {table_name}.\n")

                sql = f"""
                       WITH RankedData AS (
                        SELECT
                            v."ID",
                            ROW_NUMBER() OVER (
                                PARTITION BY v."UserSignalID", date_trunc('minute', v."Time")
                                ORDER BY v."Time" ASC   -- dakika içinde ilk gelen kaydı bırak
                            ) AS "RowRank"
                        FROM dbo."{table_name}" v
                        JOIN dbo."UserSignals" us ON v."UserSignalID" = us."UserSignalID"
                        JOIN dbo."Signals" s ON us."SignalID" = s."SignalID"
                        WHERE 
                            v."Time" >= %(start_date)s
                            AND v."Time" < %(end_date)s
                            AND NOT EXISTS (
                                SELECT 1
                                FROM dbo."ExcludedSignals" sc
                                WHERE sc."CleaningSignalID" = s."SignalID"
                            )
                    )
                    DELETE FROM dbo."{table_name}"
                    WHERE "ID" IN (
                        SELECT "ID"
                        FROM RankedData
                        WHERE "RowRank" > 1
                    );
                """

                cur.execute(sql, params)
                deleted_count = cur.rowcount
                conn.commit()

                end_time = datetime.datetime.now()
                duration = end_time - start_time

                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(
                        f"[{end_time}] Cleanup finished for {table_name}. "
                        f"{deleted_count} kayıt silindi. "
                        f"Süre: {duration}.\n"
                    )

                send_email(
                    f"Cleanup Completed for {table_name}",
                    f"Toplam {deleted_count} kayıt silindi.\n"
                    f"Başlangıç: {start_time}\n"
                    f"Bitiş: {end_time}\n"
                    f"Geçen Süre: {duration}"
                )

    except Exception as e:
        end_time = datetime.datetime.now()
        error_msg = f"[{end_time}] Cleanup failed for {table_name}: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(error_msg + "\n")
        send_email(f"Cleanup Failed for {table_name}", error_msg)

# Ana fonksiyon
if __name__ == "__main__":
    try:
        # Şu anki zaman
        now = datetime.datetime.now()

        # Bir gün öncesi (dün)
        yesterday = now - datetime.timedelta(days=1)

        # Dün 00:00
        start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)

        # Dün 23:59:59
        end_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)

        params = {
            "interval_minute": 1,
            "start_date": start_date,
            "end_date": end_date,
        }

        # Birden fazla tablo için çağırılabilir
        run_cleanup_for_table("Values", params)

        time.sleep(60)  # gerekiyorsa bekleme
         
        run_cleanup_for_table("Values_Perm", params)

    except Exception as e:
        error_msg = f"[{datetime.datetime.now()}] Main cleanup script failed: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(error_msg + "\n")
        send_email("Cleanup Script Failed", error_msg)
