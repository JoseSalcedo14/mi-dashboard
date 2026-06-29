# Mi Dashboard personal — auto-actualizable e independiente

Un dashboard online que se actualiza solo y **no depende de Claude, Cowork ni ninguna suscripción**.
Una vez desplegado, corre por sí mismo en infraestructura gratis de GitHub.

## Cómo funciona

```
Google Calendar (ICS)  ┐
                       ├─► GitHub Actions (cron cada hora) ─► data.json ─► GitHub Pages (web pública)
Google Sheet (CSV)     ┘        build_data.py
```

- **GitHub Pages** sirve el `index.html` en una URL fija. Lo abres desde cualquier navegador, móvil o PC.
- **GitHub Actions** corre `build_data.py` cada hora, regenera `data.json` y lo publica. Sin servidor, $0.
- **Tus datos**: calendario vía la dirección ICS secreta de Google Calendar; tareas/finanzas/métricas vía un Google Sheet que editas a mano desde donde sea (esa es tu "entrada manual").
- **Sin claves ni APIs**: todo usa URLs públicas de solo lectura. Cero OAuth.

## Despliegue (≈10 min)

1. **Crea un repo** en GitHub (puede ser privado) y sube estos archivos manteniendo la estructura:
   ```
   index.html
   data.json
   build_data.py
   .github/workflows/update-dashboard.yml
   ```
2. **Activa Pages**: Settings → Pages → Source: `Deploy from a branch` → rama `main`, carpeta `/ (root)`. Tu dashboard quedará en `https://TU_USUARIO.github.io/TU_REPO/`.
3. **Conecta el calendario** (opcional): Google Calendar → Configuración del calendario → *Integrar calendario* → copia la **"Dirección secreta en formato iCal"**. En el repo: Settings → Secrets and variables → Actions → New secret → nombre `CAL_ICS_URL`, valor la URL.
4. **Conecta tareas/finanzas/métricas** (opcional): crea un Google Sheet con columnas `section,title,meta,value,status`. Publícalo: Archivo → Compartir → *Publicar en la web* → CSV. Copia la URL y guárdala como secret `SHEET_CSV_URL`.
5. **Activa permisos del workflow**: Settings → Actions → General → Workflow permissions → *Read and write*.
6. Corre el workflow una vez a mano (pestaña Actions → *Actualizar dashboard* → *Run workflow*). Listo.

## Formato del Google Sheet

| section  | title             | meta | value  | status |
|----------|-------------------|------|--------|--------|
| tareas   | Cerrar propuesta  | Alfa | Hoy    | due    |
| finanzas | Comida            |      | -310   |        |
| metricas | Pasos hoy         | 74   | 7,420  |        |

- `status` para tareas: `due` (rojo), `soon` (ámbar), `ok` (verde).
- En `finanzas`, monto en `value` (negativo = gasto).
- En `metricas`, `meta` = % para la barra (0–100), `value` = texto a mostrar.

## Personalizar

- **Frecuencia**: edita el `cron` en el workflow (`0 * * * *` = cada hora; `*/15 * * * *` = cada 15 min).
- **Estilo**: colores en el bloque `:root` de `index.html`.
- **Más fuentes** (Notion, Asana, banca, etc.): se añaden como funciones nuevas en `build_data.py`. Algunas sí requieren API key (se guardan como secrets). Podemos hacerlo en una segunda iteración.

## El rol de Claude (opcional)

No es necesario para que corra, pero si quieres puedes pedirle a Claude que edite el HTML, agregue fuentes o cambie el diseño cuando gustes. El dashboard sigue funcionando aunque nunca vuelvas a abrir Claude.
