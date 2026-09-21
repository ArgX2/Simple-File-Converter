# Simple File Converter

[한국어](README.md) | [English](README.en.md) | [日本語](README.ja.md) | [简体中文](README.zh-CN.md) | **Español**

Conversor de archivos para Windows. Versión actual: `v1.0.0`. Arrastra o selecciona archivos, elige el formato de salida y conviértelos. También puedes convertir un solo archivo desde el menú contextual del Explorador. Consulta el [historial de cambios](CHANGELOG.md).

## Descargas

| Opción | Descarga | Detalles |
| --- | --- | --- |
| **EXE portátil** | [Descargar para Windows](https://github.com/ArgX2/Simple-File-Converter/releases) | Selecciona **Assets → Simple File Converter.exe** en una versión publicada. No requiere instalación. |
| **Código fuente ZIP** | [Descargar código fuente](https://github.com/ArgX2/Simple-File-Converter/archive/refs/heads/main.zip) | Código más reciente de la rama main. Necesitas Python para ejecutarlo. |
| **Explorar el código** | [Ver en GitHub](https://github.com/ArgX2/Simple-File-Converter/tree/main/src) | Consulta el código sin descargarlo. |

> El EXE se puede descargar una vez adjuntado a una versión publicada. Si la lista de versiones está vacía, aún no se ha publicado ningún ejecutable. Para obtener el código de una versión concreta, selecciona **Source code (zip)** en esa versión.

Descarga y ejecuta el EXE, y arrastra los archivos a la ventana. Consulta los requisitos para las conversiones que necesitan software de Office.

## Funciones principales

- Conversión de vídeo, audio, imágenes y PDF
- Conversión por lotes y cancelación
- Guardar en una carpeta elegida o junto a cada archivo original
- Conservación de originales y numeración automática si el nombre de salida ya existe
- Explorador: clic derecho → **Simple File Converter** → formato de salida
- Resaltado al arrastrar y notificaciones de información, éxito y error con distintos colores
- Versión portátil en un solo EXE
- Detección del idioma del sistema y selección entre 16 idiomas de interfaz

### Configuración del idioma

En **Idioma**, abajo a la izquierda, elige **Automático (idioma del sistema)** o un idioma concreto. El cambio se aplica inmediatamente sin borrar la lista ni los resultados. Se conserva para los siguientes inicios y para las conversiones desde el menú contextual. Durante una conversión no se puede cambiar el idioma.

Idiomas disponibles: coreano, inglés, japonés, chino simplificado y tradicional, alemán, francés, español, portugués, italiano, ruso, vietnamita, tailandés, indonesio, árabe y hebreo. El árabe y el hebreo usan una disposición de derecha a izquierda. Si el idioma del sistema no está disponible, se utiliza el inglés.

Las traducciones están incluidas en el EXE y funcionan sin conexión. La preferencia se guarda para el usuario actual de Windows y se mantiene al mover el EXE. Los diálogos nativos de Windows y los errores originales de programas externos pueden aparecer en su propio idioma. Las traducciones no han sido revisadas por hablantes nativos; las correcciones son bienvenidas.

## Requisitos

- Windows 10/11 de 64 bits
- Para ejecutar o compilar desde el código fuente: Python 3.12 de 64 bits
- PPT/PPTX → PDF y PDF → PPT: **requieren PowerPoint o LibreOffice instalado**
- PDF → PPTX: no requiere Office. Cada página se guarda como una **diapositiva de imagen**; el texto y las formas no se recuperan como objetos editables por separado.

## Formatos compatibles

| Entrada | Salida |
| --- | --- |
| MP4, AVI, MKV, MOV, WEBM, WMV, M4V, MPG, MPEG | MP4, AVI, MKV, MOV, WEBM, GIF, PNG, JPG y extracción de audio |
| MP3, WAV, FLAC, AAC, M4A, OGG, OPUS, WMA | MP3, WAV, FLAC, M4A, OGG, AAC, OPUS |
| PNG, JPG, JPEG, GIF, WEBP, BMP, TIF, TIFF, ICO | PNG, JPG, WEBP, BMP, TIFF, GIF, PDF |
| PDF | PNG, JPG, WEBP, TIFF, PPTX, PPT |
| PPT, PPTX | PDF |

La disponibilidad de cada conversión depende del contenido del archivo y del software instalado. La conversión de GIF animado a MP4/WEBM se puede seleccionar en la ventana del programa.

Las conversiones que no pueden conservar completamente el original se muestran como `Convertir a XXX de forma incompleta`.

### Estado de las conversiones

`O` significa conversión normal, `△` significa conversión incompleta en la que pueden cambiar el contenido, la calidad o la estructura, y `X` significa que no es compatible.

| Entrada \\ Salida | Imágenes | Vídeo | Audio | PDF | PPTX | PPT |
| --- | --- | --- | --- | --- | --- | --- |
| PNG/JPG/GIF y otras imágenes | O/△ | △ | X | O | X | X |
| MP4/AVI y otros vídeos | △ | △ | △ | X | X | X |
| MP3/WAV y otros audios | X | X | △ | X | X | X |
| PDF | △ | X | X | X | △ | △ |
| PPT/PPTX | X | X | X | △ | X | X |

Los formatos de salida concretos aparecen en la tabla de formatos compatibles y pueden variar según el contenido y el software de Office instalado.

## Uso

1. Arrastra archivos a la ventana o pulsa **Elegir archivos**.
2. Selecciona el formato de salida de cada archivo.
3. Elige una carpeta de salida o activa **Junto a los originales**.
4. Pulsa **Convertir**.

<img width="1450" height="1007" alt="Ventana del programa con la interfaz en coreano" src="https://github.com/user-attachments/assets/5b0fcd4a-2e55-440a-aa7e-3615843dfaf8" />

Haz doble clic en un elemento con error para ver los detalles. Las notificaciones se cierran tras 2,5 segundos. Al elegir Sí en la confirmación relacionada con presentaciones, no se volverá a preguntar hasta vaciar completamente la lista.

### Menú contextual del Explorador

Activa **Activar menú de conversión de Explorer** en la parte inferior del programa. En Windows 11 aparece dentro de **Mostrar más opciones**. Al seleccionar un formato, el resultado se guarda en la misma carpeta que el original.

- Procesa un archivo a la vez.
- Las opciones se basan en la extensión; el contenido se comprueba después. Por ejemplo, extraer audio de un vídeo sin sonido puede fallar.
- El menú se registra para el usuario actual de Windows. Al desactivarlo, solo se eliminan las entradas de esta aplicación.
- Desactiva el menú antes de mover o borrar el EXE. Si lo has movido, desactiva y reactiva la opción desde la nueva ubicación para registrarla de nuevo.

<img width="814" height="273" alt="Menú contextual de conversión en coreano" src="https://github.com/user-attachments/assets/2f93bf9b-7e86-4e5b-b456-e4f97161345c" />

## Ejecutar desde el código fuente

Ejecuta estos comandos en PowerShell desde la raíz del repositorio. No es necesario activar el entorno virtual.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe src\app.py
```

Los archivos se convierten localmente. La instalación inicial de dependencias necesita conexión a internet. La página de inicio de sesión de Microsoft solo se abre si aceptas el aviso correspondiente.

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Las pruebas generan archivos en carpetas temporales. Las pruebas del registro usan un sustituto en memoria y no modifican el menú real del Explorador. La conversión con Office y la integración con el Explorador requieren comprobaciones manuales adicionales.

## Compilar un EXE portátil

```powershell
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm "Simple File Converter.spec"
```

Resultado: `dist/Simple File Converter.exe`

```powershell
& ".\dist\Simple File Converter.exe" --self-test ".\build\smoke-check"
& ".\dist\Simple File Converter.exe" --smoke-test
```

`--self-test` escribe los resultados en `report.json`, dentro de la carpeta indicada. Consulta la [guía de desarrollo](docs/DEVELOPMENT.md) para más información sobre compilación y publicación (en coreano).

## Limitaciones

- PDF → imágenes: renderiza todas las páginas a 144 ppp en una carpeta independiente.
- Vídeo → PNG/JPG e imagen animada → PNG/JPG/BMP: solo guarda el primer fotograma.
- Vídeo → GIF: 12 fps y ancho máximo de 720 px.
- Usa las primeras pistas de vídeo y audio; no copia subtítulos ni pistas adicionales.
- Iniciar sesión en el navegador puede no resolver los problemas de conexión o activación de Office ni los errores de sesión de Windows.
- El EXE portátil extrae los archivos necesarios a una carpeta temporal y los elimina al salir.

## Estructura del proyecto

```text
src/                       Código de la aplicación e icono
tests/                     Pruebas automatizadas
docs/                      Guías de uso, desarrollo y publicación
licenses/                  Avisos de licencias de terceros
.github/                   CI de Windows y plantillas de issues/PR
Simple File Converter.spec Configuración de compilación portátil
```

## Estado de la licencia

**Todavía no se ha asignado una licencia pública al código propio del proyecto.** No debe suponerse que se aplica MIT u otra licencia hasta que el propietario elija una.

Las condiciones de terceros se aplican por separado. PyMuPDF/MuPDF ofrece [licencia AGPL o comercial](https://pymupdf.readthedocs.io/en/latest/about.html#license-and-copyright), y las [condiciones de FFmpeg dependen de la configuración de compilación](https://ffmpeg.org/legal.html). Antes de distribuir públicamente, revisa la licencia del proyecto y los requisitos de entrega del código fuente de la compilación concreta. Consulta [THIRD_PARTY.txt](THIRD_PARTY.txt) y la [lista de comprobación para publicar](docs/RELEASING.md) (en coreano).
