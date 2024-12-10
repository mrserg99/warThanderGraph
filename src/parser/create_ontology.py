import json
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF
import urllib.parse

def normalize_name(name):
    """Заменяет пробелы и другие недопустимые символы для формирования корректного URI."""
    return urllib.parse.quote(name.replace(" ", "_"))

# Пространство имен
NS = Namespace("http://example.org/war_thunder#")

# Создаем граф
g = Graph()

# Открытие JSON
with open("../../recourse/final_eng.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Парсинг данных
aviation_class = URIRef(NS["Aviation"])
g.add((aviation_class, RDF.type, NS.Class))

for aircraft_type, aircraft_list in data["aviation"].items():
    aircraft_type_class = URIRef(NS[aircraft_type.replace(" ", "_")])
    g.add((aircraft_type_class, RDF.type, NS.Class))
    g.add((aviation_class, NS.hasType, aircraft_type_class))

    for aircraft in aircraft_list:
        # Создание индивидуала для самолета
        aircraft_individual = URIRef(NS[normalize_name(aircraft["name"])])
        g.add((aircraft_individual, RDF.type, aircraft_type_class))
        g.add((aircraft_individual, NS.hasType, Literal(aircraft["type"])))
        g.add((aircraft_individual, NS.hasCountry, URIRef(NS[aircraft["country"].lower()])))
        g.add((aircraft_individual, NS.hasRank, URIRef(NS[f"Rank_{aircraft['rank']}"])))
        g.add((aircraft_individual, NS.hasPrice, Literal(aircraft["price"])))

        # Парсинг режимов
        for mode, mode_data in aircraft["modes"].items():
            mode_class = URIRef(NS[mode])
            mode_individual = URIRef(NS[f"{normalize_name(aircraft['name'])}_{mode}"])
            g.add((mode_individual, RDF.type, mode_class))
            g.add((aircraft_individual, NS.hasMode, mode_individual))

            # Парсинг статистики, бонусов и ремонта
            for category, props in mode_data.items():
                category_class = URIRef(NS[category])
                category_individual = URIRef(NS[f"{normalize_name(aircraft['name'])}_{mode}_{category}"])
                g.add((category_individual, RDF.type, category_class))
                g.add((mode_individual, NS[f"has{category.capitalize()}"], category_individual))

                # Добавление свойств
                for key, value in props.items():
                    if value is None:
                        value = 0  # Заменяем null на 0
                    g.add((category_individual, NS[key], Literal(value)))

# Сохраняем в файл Turtle
with open("aviation.ttl", "w", encoding="utf-8") as ttl_file:
    ttl_file.write(g.serialize(format="turtle"))