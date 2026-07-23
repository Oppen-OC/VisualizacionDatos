# Guion — Airbnb Madrid (≈ 3 min)

_Revisado: corregido el hallazgo precio↔rating (antes afirmaba lo contrario) y añadida la sección "Hosts profesionales". Recortado para mantener ~3 min._

---

**[En pantalla: portada — el mapa]**

Analicé el mercado de Airbnb en Madrid con datos de Inside Airbnb, un proyecto independiente y sin ánimo de lucro que publica información de los anuncios reales de la plataforma para estudiar el impacto del alquiler turístico. De Madrid, junio de 2026: más de veintidós mil anuncios, un millón y medio de reseñas y el calendario de un año entero, más de ocho millones de filas.

Primero los limpié con Python y pandas: precios que venían como texto, valores faltantes tratados según su causa —un quince por ciento de anuncios sin precio, que decidí no inventar— y barrios y coordenadas validados. Con los datos limpios construí un cuadro de mando interactivo en Streamlit. Estos son los hallazgos.

**[Pestaña "Qué fija el precio"]**

El precio no lo marca la calidad, sino el tamaño: la capacidad pesa seis veces más que la valoración de los huéspedes. Un piso entero cuesta de media ciento cuarenta y tres euros por noche; una habitación privada, sesenta y cuatro; una compartida, veinticinco. Y la ubicación importa: Salamanca y Centro doblan a la periferia, aunque ese sobreprecio se desvanece a tres kilómetros de la Puerta del Sol.

Y aquí el dato que más me sorprendió, porque va contra la intuición: pagar más **no** compra mejores reseñas. El precio explica menos del uno por ciento de la valoración; el efecto existe, pero es diminuto. Lo que de verdad predice una buena nota no es cuánto cuesta el piso, sino **quién** lo gestiona. Y a eso vuelvo.

**[Pestaña "La demanda"]**

Usando las reseñas como aproximación de las estancias, el turismo no solo se recuperó de la pandemia: se disparó. Cayó un sesenta y nueve por ciento en 2020 y en 2025 registró cuatro veces más reseñas que antes del COVID. Y Madrid es destino urbano, no de playa: el mes más fuerte es octubre y el más flojo, agosto, en pleno verano. El calendario de reservas futuras confirma el patrón.

**[Pestaña "Quién manda"]**

Airbnb ya no es cosa de particulares: un tercio de los anuncios está en manos de anfitriones con más de veinte pisos; el mayor gestiona cuatrocientos cuarenta y nueve. Los Superhosts apenas cobran más, pero reciben casi el triple de reseñas al mes: su distintivo se traduce en ocupación, no en precio. Y dos de cada tres anuncios declaran licencia, con el centro cumpliendo más que la periferia, donde operan los grandes gestores.

**[Pestaña "Hosts profesionales"]**

Esto enlaza con lo que prometí: quien predice la nota es el anfitrión, no el precio. Cuanto más profesional es, peor lo valoran. Y lo revelador es **dónde** falla: al pasar del particular al gran gestor, la comunicación y el check-in se desploman, mientras la ubicación —lo único que no puede cambiar— apenas se mueve. Lo que se pierde al escalar es el trato humano, no el piso. Y encima cobra menos por persona: compite con volumen, no con calidad. El patrón aguanta comparando pisos del mismo barrio y tipo, así que no es un espejismo de zona.

**[Vuelta al mapa]**

En resumen: el precio lo marcan el tamaño y la ubicación, no la calidad; la demanda está en máximos históricos; y el mercado se profesionaliza a costa de la experiencia del huésped. Todo se explora en el dashboard, filtrando por barrio, tipo de alojamiento y anfitrión. Gracias.
