
from database import DatabaseManager

def list_airlines():
    try:
        db = DatabaseManager()
        conn = db.get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT airline_code, COUNT(*) as c FROM flights GROUP BY airline_code ORDER BY c DESC LIMIT 20")
            results = cursor.fetchall()
            print("Top 20 Airlines:")
            for r in results:
                print(f"{r['airline_code']}: {r['c']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_airlines()
