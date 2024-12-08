import pandas
from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, URLField, TimeField, SelectField, validators
from wtforms.validators import DataRequired
import csv

'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)


class CafeForm(FlaskForm):
    cafe = StringField('Cafe name', validators=[DataRequired()])
    map = URLField(label='Location', validators=[DataRequired(), validators.URL()])
    open = TimeField(label='Opens At', validators=[DataRequired()])
    close = TimeField(label='Closes At', validators=[DataRequired()])
    coffee = SelectField(
        label='Coffee Rating',
        choices=[
            ('☕️☕️☕️☕️☕️', '☕️☕️☕️☕️☕️'),
            ('☕️☕️☕️☕️', '☕️☕️☕️☕️'),
            ('☕️☕️☕️', '☕️☕️☕️'),
            ('☕️☕️', '☕️☕️'),
            ('☕️', '☕️')
        ]
    )
    wifi = SelectField(
        label='Wifi Rating',
        choices=[
            ('💪💪💪💪💪', '💪💪💪💪💪'),
            ('💪💪💪💪', '💪💪💪💪'),
            ('💪💪💪', '💪💪💪'),
            ('💪💪', '💪💪'),
            ('💪', '💪'),
            ('❌', '❌')
        ]
    )
    power = SelectField(
        label='Power Rating',
        choices=[
            ('🔌🔌🔌🔌🔌', '🔌🔌🔌🔌🔌'),
            ('🔌🔌🔌🔌', '🔌🔌🔌🔌'),
            ('🔌🔌🔌', '🔌🔌🔌'),
            ('🔌🔌', '🔌🔌'),
            ('🔌', '🔌'),
            ('❌', '❌')
        ]
    )
    submit = SubmitField('Submit')

# Exercise Done


# all Flask routes below
@app.route("/")
def home():
    return render_template("index.html")


@app.route('/add', methods=['GET', 'POST'])
def add_cafe():
    form = CafeForm()
    if form.validate_on_submit():
        with open('cafe-data.csv', mode='a', newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(
                [f"{form.cafe.data}",
                 f"{form.map.data}",
                 f"{form.open.data}",
                 f"{form.close.data}",
                 f"{form.coffee.data}",
                 f"{form.wifi.data}",
                 f"{form.power.data}"]
            )
    # Exercise:
    # Done
    return render_template('add.html', form=form)


@app.route('/cafes')
def cafes():
    with open('cafe-data.csv', newline='', encoding='utf-8') as csv_file:
        csv_data = csv.reader(csv_file, delimiter=',')
        list_of_rows = []
        for row in csv_data:
            list_of_rows.append(row)
    return render_template('cafes.html', cafes=list_of_rows)


if __name__ == '__main__':
    app.run(debug=True)
