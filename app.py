import sqlite3


def get_connection():
    return sqlite3.connect("pc_hardware.db")


def show_menu():
    print("\n" + "=" * 45)
    print("      СУБД ПК КОМПЛЕКТУЮЧІ (v3.1 Stable)")
    print("=" * 45)
    print("1. 📋 Переглянути всі деталі")
    print("2. ➕ Додати нову деталь")
    print("3. 🖥️ Автоматичний підбір збірки за бюджетом")
    print("4. 📊 Статистика складу")
    print("5. ❌ Вийти")
    print("-" * 45)


def list_all(conn):
    cursor = conn.cursor()
    query = """
    SELECT components.name, components.price, categories.name 
    FROM components 
    JOIN categories ON components.category_id = categories.id;
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    if not rows:
        print("\n⚠️ База даних порожня!")
        return

    print("\n" + "-" * 55)
    print(f"{'Деталь':<25} | {'Ціна (грн)':<12} | {'Категорія':<12}")
    print("-" * 55)
    for r in rows:
        print(f"{r[0]:<25} | {r[1]:<12} | {r[2]:<12}")
    print("-" * 55)


def add_item(conn):
    cursor = conn.cursor()

    while True:
        name = input("Назва деталі: ").strip()
        if name:
            break
        print("❌ Помилка! Назва не може бути порожньою.")

    while True:
        try:
            price = int(input("Ціна (грн): "))
            if price <= 0:
                print("❌ Помилка! Ціна має бути більше 0 грн.")
                continue
            break
        except ValueError:
            print("❌ Помилка! Введіть ціле число.")

    print("\nДоступні категорії: 1 - Процесори | 2 - Відеокарти | 3 - SSD")
    while True:
        try:
            cat_id = int(input("ID категорії (1-3): "))
            if cat_id in [1, 2, 3]:
                break
            print("❌ Помилка! Оберіть категорію строго від 1 до 3.")
        except ValueError:
            print("❌ Помилка! Введіть число від 1 до 3.")

    cursor.execute(
        "INSERT INTO components (name, price, category_id) VALUES (?, ?, ?)",
        (name, price, cat_id),
    )
    conn.commit()
    print(f"\n✅ Успішно додано: {name} за {price} грн")


def build_pc_by_budget(conn):
    while True:
        try:
            budget = int(input("\nВведіть ваш бюджет на ПК (грн): "))
            if budget <= 0:
                print("❌ Бюджет має бути більше 0 грн.")
                continue
            break
        except ValueError:
            print("❌ Помилка! Введіть ціле число.")

    cursor = conn.cursor()

    query = """
    SELECT 
        cpu.name, cpu.price,
        gpu.name, gpu.price,
        ssd.name, ssd.price,
        (cpu.price + gpu.price + ssd.price) AS total_price
    FROM 
        (SELECT name, price FROM components WHERE category_id = 1) cpu,
        (SELECT name, price FROM components WHERE category_id = 2) gpu,
        (SELECT name, price FROM components WHERE category_id = 3) ssd
    WHERE 
        (cpu.price + gpu.price + ssd.price) <= ?
    ORDER BY 
        total_price DESC
    LIMIT 1;
    """

    cursor.execute(query, (budget,))
    build = cursor.fetchone()

    if not build:
        print(
            f"\n⚠️ На бюджет {budget} грн не вдалося зібрати ПК. У базі немає достатньо дешевих комплектуючих під цей бюджет."
        )
        return

    cpu_name, cpu_price, gpu_name, gpu_price, ssd_name, ssd_price, total = (
        build
    )

    print("\n" + "=" * 50)
    print(f"🎯 ОПТИМАЛЬНА ЗБІРКА ПІД БЮДЖЕТ {budget} ГРН:")
    print("=" * 50)
    print(f"🔹 Процесор:   {cpu_name:<22} ({cpu_price} грн)")
    print(f"🔹 Відеокарта: {gpu_name:<22} ({gpu_price} грн)")
    print(f"🔹 Накопичувач: {ssd_name:<22} ({ssd_price} грн)")
    print("-" * 50)
    print(f"💰 Загальна вартість: {total} грн")
    print(f"💵 Залишок:          {budget - total} грн")
    print("=" * 50)


def show_stats(conn):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*), COALESCE(SUM(price), 0), COALESCE(AVG(price), 0) FROM components;"
    )
    total_count, total_sum, avg_price = cursor.fetchone()

    if total_count == 0:
        print("\n📊 База даних порожня. Статистика відсутня.")
        return

    cursor.execute(
        "SELECT name, MAX(price) FROM components;"
    )
    max_item, max_price = cursor.fetchone()

    print("\n📊 СТАТИСТИКА БАЗИ ДАНИХ:")
    print("-" * 40)
    print(f"Всього позицій на складі: {total_count}")
    print(f"Загальна вартість товарів: {total_sum} грн")
    print(f"Середня ціна деталі:     {round(avg_price, 2)} грн")
    print(f"Найдорожчий товар:        {max_item} ({max_price} грн)")
    print("-" * 40)


def main():
    conn = get_connection()
    while True:
        show_menu()
        choice = input("Оберіть дію (1-5): ").strip()

        if choice == "1":
            list_all(conn)
        elif choice == "2":
            add_item(conn)
        elif choice == "3":
            build_pc_by_budget(conn)
        elif choice == "4":
            show_stats(conn)
        elif choice == "5":
            print("З'єднання з базой закрито. Бувай!")
            break
        else:
            print("❌ Невірний вибір. Введіть цифру від 1 до 5.")

    conn.close()


if __name__ == "__main__":
    main()