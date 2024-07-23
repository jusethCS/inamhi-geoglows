0 5 * * * sh /home/ubuntu/inamhi-geoglows/taskfiles/meteosat/r_daily.sh > /home/ubuntu/logs/daily.log

5,15,25,35,45,55 * * * * /home/ubuntu/miniconda3/envs/goes/bin/python /home/ubuntu/inamhi-geoglows/taskfiles/goes/goes_cmipf_1-7.py > /home/ubuntu/logs/goes_1-7.log
0,10,20,30,40,50 * * * * /home/ubuntu/miniconda3/envs/goes/bin/python /home/ubuntu/inamhi-geoglows/taskfiles/goes/goes_cmipf_8-16.py > /home/ubuntu/logs/goes_8-16.log

0 13 * * * /home/ubuntu/miniconda3/envs/geoglows/bin/python /home/ubuntu/inamhi-geoglows/taskfiles/fireforest/daily_pacum.py > /home/ubuntu/logs/fireforest_pacum.log
0 8 * * * /home/ubuntu/miniconda3/envs/geoglows/bin/python /home/ubuntu/inamhi-geoglows/taskfiles/geoglows_v01/update_ensemble_forecast.py > /home/ubuntu/logs/update_ensemble_forecast.log
0 8 * * * /home/ubuntu/miniconda3/envs/geoglows/bin/python /home/ubuntu/inamhi-geoglows/taskfiles/geoglows_v01/update_forecast_records.py > /home/ubuntu/logs/update_forecast_records.log



