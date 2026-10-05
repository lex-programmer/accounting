from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_codbugetar_liniebugetara_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='liniabugetaracalc',
            name='sursa',
            field=models.CharField(
                choices=[
                    ('camin', 'Cămin'),
                    ('licenta', 'Licență'),
                    ('macter', 'Macter'),
                    ('doctorat', 'Doctorat'),
                    ('colegiu', 'Colegiu'),
                    ('colegiu_camin', 'Colegiu cămin'),
                    ('cursuri', 'Cursuri'),
                    ('cantina', 'Cantină'),
                    ('arenda', 'Arendă'),
                    ('catedra_militara', 'Catedră militară'),
                    ('alte', 'Alte'),
                    ('dobinda_din_depozit', 'Dobândă din depozit'),
                    ('finantare_complem', 'Finanțare complementară'),
                    ('nortek', 'Nortek'),
                    ('autoguvernanti', 'Autoguvernanți'),
                    ('stiinta_mec', 'Știință MEC'),
                    ('colegiu_extern', 'Colegiu extern'),
                    ('colegiu_extern_camin', 'Colegiu extern cămin'),
                    ('sponsorizare', 'Sponsorizare'),
                    ('stiinta_ancd', 'Știință ANCD'),
                    ('banca_mondiala', 'Banca Mondială'),
                    ('proicte_externe', 'Proiecte externe'),
                ],
                default='',
                max_length=100,
            ),
            preserve_default=False,
        ),
    ]
