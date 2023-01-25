import schedule
from parser import parse_url
from main import db
from models import Item, ProductPrice, Message, User
from datetime import datetime
import time


def main():
    users_id = [user.id for user in db.session.query(User).filter_by(get_notifications=True).all()]
    for user_id in users_id:
        items = db.session.query(Item).filter_by(user_id=user_id).all()
        messages = []
        for item in items:
            last_price = db.session.query(ProductPrice).filter_by(item_id=item.id).order_by(
                ProductPrice.id.desc()).first().price
            current_price = parse_url(item.url)[2]
            last_price = str(last_price).replace(' ', '')
            current_price = str(current_price).replace(' ', '')
            price = ProductPrice(
                item_id=item.id,
                price=current_price,
                date=datetime.now()
            )
            db.session.add(price)
            db.session.commit()
            if int(last_price) > int(current_price):
                messages.append(f'Цена на {item.product} снизилась c {last_price} до {current_price}')
            elif int(last_price) < int(current_price):
                messages.append(f'Цена на {item.product} поднялась c {last_price} до {current_price}')
            elif int(last_price) == int(current_price):
                messages.append('no changes')
        for message in messages:
            msg = Message(
                message=message,
                user_id=user_id
            )
            db.session.add(msg)
        db.session.commit()


if __name__ == '__main__':
    schedule.every().day.at('11:00').do(main)
    while True:
        schedule.run_pending()
        time.sleep(1)
