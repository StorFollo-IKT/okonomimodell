**Sørg for at kildedata er oppdatert:**
- Sjekk at filene på datagrunnlag er oppdatert: `ls -l /home/datagrunnlag`

 - Last inn data:
`./load_data.sh`
 - Kjør manuell import fra PureService og se at det ikke er noen feil:
`python3 manage.py pus_workstations`

**Lag dokumentasjon på fakturagrunnlag**
```
python3 manage.py export_workstations
python3 manage.py export_products
```

**Lag faktura**
- Opprett faktura i administrasjonspanelet
- Kjør ønskede invoice_* management commands for å produsere linjer:
```
python3 manage.py invoice_user_products -t "Arbeidsflateabonnement"
python3 manage.py invoice_product_deliveries
python3 manage.py invoice_workstations
python3 manage.py invoice_applications
```

- Kjør `python3 manage.py invoice_export_excel` for å eksportere fakturagrunnlaget

