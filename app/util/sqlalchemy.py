#!/usr/local/bin/python
# -*- coding: utf-8 -*-
"""
    app.util.sqlalchemy
    ~~~~~~~~~~~

    Utility module for SQLAlchemy


    :copyright: (c) 2019 by Ykjam Aragatnashyk (ykjam.tm).
    :license: MIT
"""

import uuid
from math import ceil

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import CHAR, TypeDecorator


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses Postgresql's UUID type, otherwise uses
    CHAR(36), storing as stringified hex values.
    """

    def process_literal_param(self, value, dialect):
        return uuid.UUID(value)

    def python_type(self):
        return uuid.UUID

    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value))
            else:
                # hex string
                return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value


class Pagination(object):
    def __init__(self, query, page=1, per_page=20):
        self.query = query
        self.page = page
        self.per_page = per_page
        self.total = query.count()
        self.items = query.limit(per_page).offset((page - 1) * per_page).all()

    @property
    def pages(self):
        """The total number of pages"""
        if self.per_page == 0:
            pages = 0
        else:
            pages = int(ceil(self.total / float(self.per_page)))
        return pages

    @property
    def prev_num(self):
        """Number of the previous page."""
        return self.page - 1

    @property
    def has_prev(self):
        """True if a previous page exists"""
        return self.page > 1

    @property
    def has_next(self):
        """True if a next page exists."""
        return self.page < self.pages

    @property
    def next_num(self):
        """Number of the next page"""
        return self.page + 1

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        """Iterates over the page numbers in the pagination.  The four
        parameters control the thresholds how many numbers should be produced
        from the sides.  Skipped page numbers are represented as `None`.
        This is how you could render such a pagination in the templates:
        .. sourcecode:: html+jinja
            {% macro render_pagination(pagination, endpoint) %}
              <div class=pagination>
              {%- for page in pagination.iter_pages() %}
                {% if page %}
                  {% if page != pagination.page %}
                    <a href="{{ url_for(endpoint, page=page) }}">{{ page }}</a>
                  {% else %}
                    <strong>{{ page }}</strong>
                  {% endif %}
                {% else %}
                  <span class=ellipsis>…</span>
                {% endif %}
              {%- endfor %}
              </div>
            {% endmacro %}
            :param left_edge: number of pages in left edge
            :param right_edge: number of pages in right edge
            :param left_current: number of pages before current page
            :param right_current: number of pages after current page
        """
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num
            elif num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num
            elif self.page - left_current - 1 < num < self.page + right_current:
                if last + 1 != num:
                    yield None
                yield num
                last = num
