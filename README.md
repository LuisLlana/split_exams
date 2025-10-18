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

	usage: python gen_latex.py [-h] [--exam EXAM] [--group GROUP] [--student_file STUDENT_FILE]

	Generate Exams to students

	options:
	  -h, --help            show this help message and exit
	  --exam EXAM           Exam template file
	  --group GROUP         Group name for the exams
	  --student_file STUDENT_FILE
	                        CSV file with students data, defaults to the argument of group ended in .csv


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
