#!/usr/bin/env bash
python3 manage.py graph_models -n --output="/home/datagrunnlag/Model graphs/Costs verbose.png" costs
python3 manage.py graph_models -n --output="/home/datagrunnlag/Model graphs/Employee info verbose.png" employee_info
python3 manage.py graph_models -n --output="/home/datagrunnlag/Model graphs/Invoice verbose.png" invoice
python3 manage.py graph_models --output="/home/datagrunnlag/Model graphs/Costs.png" costs
python3 manage.py graph_models --output="/home/datagrunnlag/Model graphs/Employee info.png" employee_info
python3 manage.py graph_models --output="/home/datagrunnlag/Model graphs/Invoice.png" invoice