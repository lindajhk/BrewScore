from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL, Length, InputRequired, ValidationError
import datetime
import csv

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfdfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)


class CafeForm(FlaskForm):
    cafe = StringField('Cafe Name', validators=[DataRequired()])
    location = StringField('Cafe Location On Google Maps (URL)', validators=[DataRequired(), URL()])
    open = StringField("Opening Time e.g. 8AM", validators=[DataRequired()])
    close = StringField("Closing Time e.g. 5:30PM", validators=[DataRequired()])
    ITEM_CHOICES = [('none_selected', 'Please select an option'), ('coffee_only', 'Coffee Only'), ('beans_only', 'Beans Only'), ('coffee_and_beans', 'Coffee and Beans')]
    item_type = SelectField('Item', choices=ITEM_CHOICES, validators=[InputRequired()])
    COFFEE_CHOICES = [('cold_brew', 'Cold Brew'), ('latte', 'Latte'), ('cappuccino', 'Cappuccino'), ('americano', 'Americano'), ('other_drink', 'Other Drink')]
    coffee_type = SelectField('Coffee Type', choices=COFFEE_CHOICES)
    other_coffee = StringField('Other Coffee', validators=[Length(max=20)])
    coffee_rating = SelectField("Coffee Rating", choices=["✘", "☕️", "☕☕", "☕☕☕", "☕☕☕☕", "☕☕☕☕☕"])
    coffee_price = SelectField("Coffee Price", choices=["✘", "💲 ($1-3)", "💲💲 ($3-5)", "💲💲💲 ($5-7)", "💲💲💲💲 ($7-10)", "💲💲💲💲💲 (oof)"])
    coffee_bean_name = StringField("Coffee Bean Name")
    coffee_bean_rating = SelectField("Coffee Bean Rating", choices=["✘", "🫘️", "🫘🫘", "🫘🫘🫘", "🫘🫘🫘🫘", "🫘🫘🫘🫘🫘"])
    coffee_bean_price = SelectField("Coffee Bean Price", choices=["✘", "💲 ($1-6)", "💲💲 ($6-15)", "💲💲💲 ($15-25)", "💲💲💲💲 ($25-35)", "💲💲💲💲💲 ($35+)"])
    comments = StringField("Comments")
    submit = SubmitField('Submit')

    def validate_field(self):
        if self.item_type.data is None or self.item_type.data == 'none_selected':
            raise ValidationError('Please select the item type')
        elif self.item_type.data == 'coffee_only':
            if self.coffee_type.data is None:
                raise ValidationError('Please select a coffee type')
            if self.coffee_rating.data is None or self.coffee_rating.data == "✘":
                raise ValidationError('Please rate the coffee')
            if self.coffee_price.data is None or self.coffee_price.data == "✘":
                raise ValidationError('Please select the price range of the coffee')
        elif self.item_type.data == 'beans_only':
            if self.coffee_bean_name.data is None or self.coffee_bean_name.data == "":
                raise ValidationError('Please enter the name of the coffee beans')
            if self.coffee_bean_rating.data is None or self.coffee_bean_rating.data == "✘":
                raise ValidationError('Please rate the coffee beans')
            if self.coffee_bean_price.data is None or self.coffee_bean_price.data == "✘":
                raise ValidationError('Please select the price range of the coffee beans')
        elif self.item_type.data == 'coffee_and_beans':
            if self.coffee_type.data is None:
                raise ValidationError('Please select a coffee type')
            if self.coffee_rating.data is None or self.coffee_rating.data == "✘":
                raise ValidationError('Please rate the coffee')
            if self.coffee_price.data is None or self.coffee_price.data == "✘":
                raise ValidationError('Please select the price range of the coffee')
            if self.coffee_bean_name.data is None or self.coffee_bean_name.data == "":
                raise ValidationError('Please enter the name of the coffee beans')
            if self.coffee_bean_rating.data is None or self.coffee_bean_rating.data == "✘":
                raise ValidationError('Please rate the coffee beans')
            if self.coffee_bean_price.data is None or self.coffee_bean_price.data == "✘":
                raise ValidationError('Please select the price range of the coffee beans')

        # Only require other coffee option if it is selected
        if self.coffee_type.data == 'other_drink' and self.other_coffee.data is None:
            raise ValidationError('Please enter drink name')


@app.route("/")
def home():
    return render_template("index.html")


@app.route('/add', methods=["GET", "POST"])
def add_cafe():
    form = CafeForm()
    if form.validate_on_submit():
        now = datetime.datetime.now()
        with open("cafe-data.csv", mode="a", encoding="utf8") as csv_file:
            csv_file.write(f"\n{form.cafe.data},"
                           f"{form.location.data},"
                           f"{form.open.data},"
                           f"{form.close.data},"
                           f"{form.other_coffee.data if form.coffee_type.data == 'other_drink' else dict(form.coffee_type.choices).get(form.coffee_type.data)},"
                           f"{form.coffee_rating.data},"
                           f"{form.coffee_price.data},"
                           f"{form.coffee_bean_name.data},"
                           f"{form.coffee_bean_rating.data},"
                           f"{form.coffee_bean_price.data},"
                           f"{now.strftime('%m-%d-%y')},"
                           f"{form.comments.data}"
                           )
        return redirect(url_for('cafes'))
    return render_template('add.html', form=form)


@app.route('/cafes')
def cafes():
    with open('cafe-data.csv', newline='', encoding="utf8") as csv_file:
        csv_data = csv.reader(csv_file, delimiter=',')
        list_of_rows = []
        for row in csv_data:
            list_of_rows.append(row)
    return render_template('cafes.html', cafes=list_of_rows)


@app.route('/remove_cafe')
def remove_cafe():
    row_index = request.args.get('cafe_id')
    if row_index is not None and row_index != '':
        with open('cafe-data.csv', 'r', newline='', encoding="utf8") as csv_file:
            csv_reader = csv.reader(csv_file)
            header = next(csv_reader)  # skip header row
            rows = [row for i, row in enumerate(csv_reader) if i != int(row_index)]
        with open('cafe-data.csv', 'w', newline='', encoding="utf8") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(header)  # write header row back to file
            csv_writer.writerows(rows)

    return redirect(url_for('cafes'))


if __name__ == '__main__':
    app.run(debug=True)
