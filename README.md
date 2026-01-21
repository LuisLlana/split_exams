# split_exams

Porgramas para generar ficheros con QR y luego separarlos cuando están
juntas todas las hojas.

Se necesitan los paquetes de python que aparecen en `requirements.txt`

## gen_latex
Programas para generar exámenes con un QR para cada alumno a
partir de un enunciado. El examen está en un fichero latex que tiene
una definición del tipo


    \newcommand{\email}{}
	\newcommand{\nombre}{}
	\newcommand{\gruoo}{}

El programa genera un fichero nuevo por cada alumno datos.

  usage: gen_latex.py [-h] [--destdir DESTDIR] -f CSVFILE exam

  Generate Exams to students

  positional arguments:
    exam                  Exam template file

  options:
    -h, --help              show this help message and exit
    --destdir DESTDIR       Destir of PDF files, defaults to exam without the suffix
    -f, --csvfile CSVFILE   CSV file with the student data

El fichero CSV es el que se descarga de GEA. Tiene el siguiente
formato
FOTOGRAFÍA,NOMBRE COMPLETO,DOCUMENTO,MAT.,CONV.,OBSERVACIÓN,CORREO,MOODLE_ID
,"Abellán Lapeña, Daniel",49147886Z,1,1,,daniab01@ucm.es,6640
,"AIT EL HAJ SABIH, HAFSA",03477456V,1,1,,hafsaait@ucm.es,6641
,"Alciturri Alvarez, Francisco Javier",06679809B,1,1,,franalci@ucm.es,6642

Sólo se usan los campos "NOMBRE COMPLETO" y "CORREO".

Los ficheros se generan en una carpeta como el nombre del grupo

## split_exams.py

Este programa recive un fichero PDF con todos los exámenes juntos.
El programa los separa. Para ello la primera página del examen debe
tener un QR con un identificador (email, por ejemplo) para cada
alumno.

	usage: python split_exams.py [-h] [--pdf PDF] [--outdir OUTDIR]

	Split exams into individual student exams.

	options:
	  -h, --help       show this help message and exit
	  --pdf PDF        PDF file to split into individual student exams.
	  --outdir OUTDIR  Output directory for individual student exams.
