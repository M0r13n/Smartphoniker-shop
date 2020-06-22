from sqlalchemy import func

from project.server.extensions import db


def default_order_index(context) -> int:
    """
    Get the current highest index
    """
    print(context)
    if context:
        try:
            return db.session.query(func.max(context.current_column.table.c.order_index)).first()[0] + 1
        except (TypeError, IndexError):
            return 0
    else:
        return 0


class OrderableMixin(object):
    """ Mixin to make database models comparable """
    order_index = db.Column(db.Integer,
                            default=default_order_index,
                            index=True)

    @classmethod
    def normalize(cls):
        """ Normalize all order indexes """
        for idx, item in enumerate(cls.query.order_by(cls.order_index).all()):
            item.order_index = idx
        db.session.commit()

    def move_up(self):
        """ Move the database object one up"""
        if self.order_index == 0:
            return

        # get all items ordered by their index
        items = self.query.order_by(self.__class__.order_index).all()
        idx = items.index(self)

        # swap with item above
        above = items[idx - 1]
        above.order_index, self.order_index = idx, above.order_index
        db.session.commit()

    def move_down(self):
        """ Move the database object one down"""

        # get all items ordered by their index
        items = self.query.order_by(self.__class__.order_index).all()
        idx = items.index(self)

        # if item is last do nothing
        if idx == len(items) - 1:
            return

        # swap with item below
        below = items[idx + 1]
        below.order_index, self.order_index = idx, below.order_index
        db.session.commit()
