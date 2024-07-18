from labbase2.models.mixins.importer import Importer
from labbase2.models.base_entity import BaseEntity
from labbase2.models import db

from datetime import date
# from reportlab.lib.units import mm


__all__ = ["Modification", "FlyStock", "Tag"]


flystock_tags = db.Table(
    "flystock_tags",
    db.Column(
        "fly_id",
        db.Integer,
        db.ForeignKey("fly_stock.id"),
        primary_key=True
    ),
    db.Column(
        "tag_id",
        db.Integer,
        db.ForeignKey("tag.id"),
        primary_key=True
    )
)


class Modification(db.Model, Importer):
    """
    Information about modification of fly stocks. This should be things
    like re-establishing a dead fly stock. If the genotype is altered it
    might be rather better to create a new fly stock entry.

    Attributes
    ----------
    id : int
        An internal identifier for this modifcation.
    fly_id : int
        The identifier of the fly stock to which this modifcation belongs.
    user_id : int
        ID of the person that did the modification.
    date : date
        Date of the modification. Defaults to the current date.
    description : str
        A short and precise explanation of what was done.

    """

    id = db.Column(db.Integer, primary_key=True)
    fly_id = db.Column(db.Integer, db.ForeignKey("fly_stock.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    date = db.Column(db.Date)
    description = db.Column(db.String(1024))


class FlyStock(BaseEntity):
    """A fly stock.

    Attributes
    ----------
    id : int
        The internal ID of this fly stock. This ID is unique among ALL entities
        in the database.
    genotype : str
        The complete genotype of this stock. Heterologeous chromosomes are
        separated by ';' and homologeous chromosomes are separated by '/'.
        The order of the chromosomes is 'x ; y ; 2 ; 3 ; 4'.
    location : str
        A string describing where this stock is located.
    created : date
        The date at which this stock was created.
    source : str
        The source of this stock. This might be either the token of the person
        that created this stock or Bloomington, VDRC, Kyoto, etc.
    document : str
        If this stock was created in our lab this should be a short
        description about how this stock was created or, even better,
        the pages in the lab book describing the generation of this stock.
    reference : str
        The DOI of a publication in which this stock was used.
    gvo : str
        The GVO classification of this stock. This will most probably be S1
        for most stock.
    rating : int
        An integer between 0 and 5 indicating how good/useful this stock is.
    discarded : date
        The date at which this stock was discarded or died out.
    tags : list of Tag
        A list of classes. Each class indicates a usage for this stock,
        e.g. 'balancer', 'UAS', 'Gal4', etc.
    complements : str
        A list of gene identifiers that form a complementation group with
        this stock. This might be of most interest for tracheal screen stocks
        but might also be a useful information for other stocks.

    """

    id = db.Column(
        db.Integer,
        db.ForeignKey("base_entity.id"),
        primary_key=True,
        info={"importable": False}
    )
    chromosome_xa = db.Column(
        db.String(512),
        nullable=False,
        default="+",
        info={"importable": True}
    )
    chromosome_xb = db.Column(
        db.String(512),
        nullable=False,
        default="+",
        info={"importable": True}
    )
    chromosome_y = db.Column(
        db.String(512),
        nullable=False,
        default="+",
        info={"importable": True}
    )
    chromosome_2a = db.Column(
        db.String(512),
        nullable=False,
        default="+",
        info={"importable": True}
    )
    chromosome_2b = db.Column(
        db.String(512),
        nullable=False,
        default="+",
        info={"importable": True}
    )
    chromosome_3a = db.Column(
        db.String(512),
        nullable=False,
        default="+",
        info={"importable": True}
    )
    chromosome_3b = db.Column(
        db.String(512),
        nullable=False,
        default="+",
        info={"importable": True}
    )
    chromosome_4a = db.Column(
        db.String(512),
        nullable=False,
        default="+",
        info={"importable": True}
    )
    chromosome_4b = db.Column(
        db.String(512),
        nullable=False,
        default="+",
        info={"importable": True}
    )
    short_genotype = db.Column(db.String(2048), info={"importable": True})
    filemaker_genotype = db.Column(db.String(2048), info={"importable": True})
    location = db.Column(db.String(64), info={"importable": True})
    created_date = db.Column(db.Date, info={"importable": True})
    source = db.Column(db.String(512), info={"importable": True})
    doc = db.Column(db.String(512), info={"importable": True})
    reference = db.Column(db.String(512), info={"importable": True})
    discarded_date = db.Column(db.Date, info={"importable": True})

    # One-to-many relationships.
    modifications = db.relationship(
        "Modification",
        backref="fly_stock",
        order_by="Modification.date.desc()",
        lazy=True
    )

    # Many-to-many relationships.
    tags = db.relationship(
        "Tag",
        secondary=flystock_tags,
        lazy="subquery",
        backref=db.backref("fly_stocks", lazy=True)
    )

    # Proper setup for joined table inheritance.
    __mapper_args__ = {"polymorphic_identity": "fly_stock"}

    def pdf(self, doc, vpos: float) -> float:

        # height, width = 297 * mm, 210 * mm
        #
        # font_color: tuple = (.3, .3, .3)
        # stroke_color: tuple = (.3, .3, .3)
        #
        # lmar: float = 5 * mm
        # rmar: float = 5 * mm
        #
        # lw: float = .3
        #
        # h1: tuple = ('Helvetica-Bold', 9)
        # h2: tuple = ('Helvetica-Bold', 7)
        # p: tuple = ('Helvetica', 7)
        #
        # values = {
        #     'Created': self.created.isoformat() if self.created else '',
        #     'Source': self.source if self.source else '',
        #     'Reference': self.reference if self.reference else ''
        # }
        #
        # doc.setStrokeColorRGB(*stroke_color)
        # doc.setFillColorRGB(*font_color)
        # doc.setLineWidth(lw)
        #
        # doc.setFont(*h1)
        # doc.drawString(lmar, vpos, self.label)
        # vpos -= 2 * mm
        #
        # doc.line(lmar, vpos, width - rmar, vpos)
        # vpos -= 6 * mm
        #
        # doc.setFont(*p)
        #
        # genotype = self.genotype_.to_tuple()
        # genotype = genotype[:1] + genotype[2:]
        #
        # w = [max([doc.stringWidth(a) for a in c]) for c in genotype]
        # w = sum(w) + 30 + doc.stringWidth(';;;')
        #
        # lpos = 105 * mm - w / 2
        #
        # for i, c in enumerate(genotype):
        #     w = max([doc.stringWidth(a.strip()) for a in c])
        #
        #     if c[0] == c[1]:
        #         doc.drawCentredString(lpos + w / 2, vpos - 2, c[0].strip())
        #     else:
        #         doc.line(lpos, vpos, lpos + w, vpos)
        #         doc.drawCentredString(lpos + w / 2, vpos + 4, c[0].strip())
        #         doc.drawCentredString(lpos + w / 2, vpos - 10, c[1].strip())
        #
        #     lpos += w
        #
        #     if not i == len(genotype) - 1:
        #         lpos += 5
        #         doc.drawString(lpos, vpos - 2, ';')
        #         lpos += 5
        #
        # # document.drawCentredString(width/2, vpos, genotype)
        # vpos -= 8 * mm
        #
        # for k, v in values.items():
        #     doc.setFont(*h2)
        #     doc.drawString(lmar, vpos, k)
        #
        #     doc.setFont(*p)
        #
        #     if not v:
        #         vpos -= 2 * mm
        #
        #     while v:
        #         for j, l in enumerate(v, start=1):
        #             if doc.stringWidth(v[:j]) > 175 * mm:
        #                 break
        #         out = v[:j]
        #         v = v[j:]
        #         doc.drawString(lmar + 20 * mm, vpos, out)
        #         vpos -= 2.5 * mm
        #
        #     vpos -= 2 * mm
        #
        # # Comments
        # doc.setFont(*h2)
        # doc.drawString(lmar, vpos, 'Comments')
        # doc.setFont(*p)
        #
        # comments = self.comments
        #
        # for i, c in enumerate(comments):
        #     v = '[{}]   {}'.format(c.person.name, c.text.strip())
        #
        #     while v:
        #         for j, l in enumerate(v, start=1):
        #             if doc.stringWidth(v[:j]) > 175 * mm:
        #                 break
        #         out = v[:j]
        #         v = v[j:].strip()
        #         doc.drawString(lmar + 20 * mm, vpos, out)
        #         if v:
        #             vpos -= 2.5 * mm
        #
        #     if not i == len(comments) - 1:
        #         vpos -= 5 * mm
        #     else:
        #         vpos -= 3 * mm
        #
        # if not comments:
        #     vpos -= 2 * mm
        #
        # doc.line(lmar, vpos, width - rmar, vpos)
        #
        # vpos -= 8 * mm

        return vpos

    @classmethod
    def _filters(cls, **fields) -> list:
        filters = []

        if not fields.pop('discarded', None):
            filters.append(cls.discarded_date.is_(None))

        if genotype := fields.pop('genotype', None):
            filters.append(cls.filemaker_genotype.ilike(genotype))

        return super()._filters(**fields) + filters


class Tag(db.Model):
    """Flies can be given classes like 'UAS' or 'signaling'. This is modeled
    as a many-to-many relationship as each stock might belong to more than
    one class and there might be several stocks belonging to the same class.

    Attributes
    ----------
    id : int
        The internal identifier of this class.
    label : str
        A short label that describes this class, e.g. 'gal4' indicating that
        this is a Gal4 driver line or 'balancer' indicating that this stock
        is thought to be used for balancing other stocks.
    description : str
        A more detailed explanation what this class is about.

    """

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(32), nullable=False)
    description = db.Column(db.String(1024), nullable=False)
