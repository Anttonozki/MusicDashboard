
from flask import Flask, render_template, jsonify, render_template_string, request
import pandas as pd
from markupsafe import Markup

app = Flask(__name__)

@app.route('/dashboard_content')
def dashboard_content():
    nombre_profesor = request.args.get('profesor')
    semana = request.args.get('semana', 'par')
    nivel = request.args.get('nivel', 'All')
    dia = request.args.get('dia', 'All')
    # Reutiliza la lógica de show_dashboard pero pasando los parámetros
    try:
        df = pd.read_csv('selecciones.csv', sep=';', engine='python')
        def title_case(s):
            return ' '.join([w.capitalize() for w in str(s).split()])

        if nombre_profesor:
            df = df[df['profesor'].str.lower() == nombre_profesor.lower()]
        if nivel != 'All':
            df = df[df['nivel'].str.lower() == nivel.lower()]
        if dia and dia != 'All':
            df = df[df['dia'].str.lower() == dia.lower()]
        if semana and semana != 'All':
            df = df[df['semana'].str.lower() == semana.lower()]

        dias_orden = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']
        df['dia_orden'] = df['dia'].str.capitalize().map({d: i for i, d in enumerate(dias_orden)})
        def hora_a_minutos(h):
            try:
                partes = str(h).split(':')
                return int(partes[0]) * 60 + int(partes[1])
            except:
                return 0
        df['hora_orden'] = df['hora'].apply(hora_a_minutos)
        df = df.sort_values(['dia_orden', 'hora_orden'])

        registros = []
        for _, row in df.iterrows():
            registro = {
                'Taller': title_case(row['taller']),
                'Día': title_case(row['dia']),
                'Hora': str(row['hora']),
                'Semana': title_case(row['semana']),
                'Nivel': title_case(row['nivel']),
                'Grado': title_case(row['grado']),
                'Subgrado': title_case(row['subgrado']),
                'Curso': title_case(row['curso']),
                'Nombres': title_case(row['nombres']),
                'Apellidos': title_case(f"{row['apellido_paterno']} {row['apellido_materno']}")
            }
            registros.append(registro)

        return render_template('_dashboard_content.html', registros=registros, profesor_seleccionado=nombre_profesor, request=request)
    except Exception as e:
        return f"<div class='alert alert-danger'>Error: {str(e)}</div>"

@app.route('/datos')
def datos():
    try:
        df = pd.read_csv('selecciones.csv', sep=';', engine='python')
        # Seleccionar y transformar los campos requeridos
        def title_case(s):
            return ' '.join([w.capitalize() for w in str(s).split()])

        campos = ['taller', 'dia', 'hora', 'semana', 'nivel', 'grado', 'subgrado', 'curso', 'nombres', 'apellido_paterno', 'apellido_materno']
        registros = []
        for _, row in df.iterrows():
            registro = {
                'Taller': title_case(row['taller']),
                'Día': title_case(row['dia']),
                'Hora': str(row['hora']),
                'Semana': title_case(row['semana']),
                'Nivel': title_case(row['nivel']),
                'Grado': title_case(row['grado']),
                'Subgrado': title_case(row['subgrado']),
                'Curso': title_case(row['curso']),
                'Nombres': title_case(row['nombres']),
                'Apellidos': title_case(f"{row['apellido_paterno']} {row['apellido_materno']}")
            }
            registros.append(registro)

        profesores = sorted(df['profesor'].dropna().unique())
        total_alumnos = df['dni'].nunique()
        return render_template('admin_datos.html', registros=registros, profesores=profesores, total_alumnos=total_alumnos, error=None)
    except Exception as e:
        error_msg = Markup(f"<b>Error al leer el archivo CSV:</b> {str(e)}<br>Por favor revisa que todas las filas tengan el mismo número de columnas y que el separador sea ';'.")
        return render_template('admin_datos.html', registros=[], profesores=[], total_alumnos=0, error=error_msg)

@app.route('/')
def index():
    return show_dashboard()

@app.route('/profesor/<nombre_profesor>')
def filtrar_profesor(nombre_profesor):
    return show_dashboard(nombre_profesor)

def show_dashboard(nombre_profesor=None):
    try:
        df = pd.read_csv('selecciones.csv', sep=';', engine='python')
        def title_case(s):
            return ' '.join([w.capitalize() for w in str(s).split()])

        if nombre_profesor:
            df = df[df['profesor'].str.lower() == nombre_profesor.lower()]

        # Ordenar por día y hora ascendente
        dias_orden = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']
        df['dia_orden'] = df['dia'].str.capitalize().map({d: i for i, d in enumerate(dias_orden)})
        # Convertir hora a formato 24h para ordenar correctamente
        def hora_a_minutos(h):
            try:
                partes = str(h).split(':')
                return int(partes[0]) * 60 + int(partes[1])
            except:
                return 0
        df['hora_orden'] = df['hora'].apply(hora_a_minutos)
        df = df.sort_values(['dia_orden', 'hora_orden'])

        registros = []
        for _, row in df.iterrows():
            registro = {
                'Taller': title_case(row['taller']),
                'Día': title_case(row['dia']),
                'Hora': str(row['hora']),
                'Semana': title_case(row['semana']),
                'Nivel': title_case(row['nivel']),
                'Grado': title_case(row['grado']),
                'Subgrado': title_case(row['subgrado']),
                'Curso': title_case(row['curso']),
                'Nombres': title_case(row['nombres']),
                'Apellidos': title_case(f"{row['apellido_paterno']} {row['apellido_materno']}")
            }
            registros.append(registro)

        profesores = sorted(df['profesor'].dropna().unique()) if not nombre_profesor else sorted(pd.read_csv('selecciones.csv', sep=';', engine='python')['profesor'].dropna().unique())
        total_alumnos = df['dni'].nunique()
        return render_template('admin_datos.html', registros=registros, profesores=profesores, total_alumnos=total_alumnos, error=None, profesor_seleccionado=nombre_profesor)
    except Exception as e:
        error_msg = Markup(f"<b>Error al leer el archivo CSV:</b> {str(e)}<br>Por favor revisa que todas las filas tengan el mismo número de columnas y que el separador sea ';'.")
        return render_template('admin_datos.html', registros=[], profesores=[], total_alumnos=0, error=error_msg, profesor_seleccionado=nombre_profesor)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
