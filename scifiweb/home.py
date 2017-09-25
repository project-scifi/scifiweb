import random
from collections import namedtuple
from textwrap import dedent

from django.shortcuts import render

import scifiweb.news.blog as blog


class Member(namedtuple('Member', ('id', 'name', 'roles', 'bio'))):
    """Represents a team member for use in the bio section."""
    @property
    def image(self):
        return 'img/members/{}.jpg'.format(self.id)

    @property
    def thumbnail(self):
        return 'img/members/thumbnails/{}.jpg'.format(self.id)


MEMBERS = (
    Member(
        'sharwood',
        'Stephen Harwood',
        ('President',),
        dedent("""
            Stephen grew up in the small town of Weaverville, California where
            he developed an interest in Chemistry and Biology. He was fortunate
            to have mentors who encouraged him to take AP Chemistry; which
            ultimately set him on a path to graduate from UC Berkeley in 2017
            with a degree in Chemical Biology. Currently, Stephen is a graduate
            student at the Scripps Research Institute pursuing a Ph.D in Organic
            Chemistry. In his free time, he enjoys exploring the outdoors on
            his dirt bike.
        """),
    ),
    Member(
        'afarzad',
        'Ali Farzad',
        ('Chief Financial Officer',),
        dedent("""
            Ali Farzad is originally from Washington, D.C, where he attended a
            high school that fostered a strong scientific background in all its
            students. He hopes to spread his passion for science and increase
            the opportunities students have to engage with this field during
            their time in high school. He currently studies Public Health at UC
            Berkeley and during his free time enjoys spending time with his
            friends.
        """),
    ),
    Member(
        'mtran',
        'Michelle Tazo Tran',
        ('Board Secretary',),
        dedent("""
            Michelle grew up in Salt Lake City, Utah and had the opportunity to
            study at the Academy for Math, Engineering & Science, a high school
            that prioritized STEM education. This school helped fuel her
            passion for the sciences, and she is currently studying at the
            University of California, Berkeley majoring in Molecular
            Toxicology. She spends the majority of her free time exploring San
            Francisco's food scene.
        """),
    ),
    Member(
        'psahrapima',
        'Parmis Sahrapima',
        ('Educational Chair',),
        dedent("""
            Parmis currently resides in Los Angeles, California where she grew
            up with a great interest for science. Being originally born and
            raised in Iran, where pursuing science was not the norm for women,
            she was determined to pursue science and medicine as a career.
            Parmis is currently a senior at UC Berkeley majoring in Molecular
            and Cell Biology, with an emphasis in Immunology and Pathogenesis.
            She has been part of the Lishko lab since December 2015, where she
            has been working on projects devoted to understanding and fixing
            male infertility. During her free time, Parmis likes to read, work
            out, and travel.
        """),
    ),
    Member(
        'spatil',
        'Shashank Patil',
        ('Chief Product Officer',),
        dedent("""
            Shashank grew up in the suburbs of Fremont, California, and
            developed an early interest in science by reading sci-fi comics and
            watching TV shows like Bill Nye. He was fortunate enough to have
            inspiring science teachers throughout primary and secondary school
            who solidified his growing interest in the health sciences. His
            mentors encouraged him to pursue his passions, which led him to
            pursue degrees in Molecular & Cell Biology, Integrative Biology,
            and Psychology in college. Since graduating, he has been working as
            an instructor and researcher in the Bay Area - both of which he
            loves.
        """),
    ),
    Member(
        'shassanin',
        'Samir Hassanin',
        ('Chief Networking Officer',),
        dedent("""
            Samir is a Bay Area local from Fremont, California. He is a fourth
            year public health student at UC Berkeley, where he discovered that
            his passion lies in health policy and management. Currently, he is
            working as an undergraduate research assistant in the Prevention
            Research Center at Stanford Medical School. Aside from conducting
            community research, Samir’s academic interests lie in teaching,
            learning, and surveying topics in comparative healthcare systems.
            In his free time, he enjoys sleeping.
        """),
    ),
    Member(
        'atreyk',
        'Atrey Koche',
        (),
        dedent("""
            Atrey grew up in the vibrant and diverse Bay Area. He attended
            Lynbrook High School where he developed an interest in the Biology,
            Chemistry, and Physics. He spent his summers working in various
            labs and offices, where his mentors inspired him to pursue his
            scientific curiosity. Currently, Atrey is pursuing a degree in
            Bioengineering at the University of California at Berkeley. In his
            spare time, Atrey likes to sing, lift weights, and play basketball.
        """),
    ),
    Member(
        'chuang',
        'Calvin Huang',
        (),
        dedent("""
            Calvin was born and raised just outside of the city of Los Angeles
            in Granada Hills, California. As a child, he loved going to The
            California Science Center, and quickly developed an interest in
            biological systems. He is currently pursuing a Bachelor of Science
            Degree in Molecular Environmental Biology at UC Berkeley. During
            the school year, Calvin is also a BASIS mentor and volunteer, where
            he teaches science lessons and shares his passion for science to
            elementary students in the Berkeley/Oakland community. In his free
            time, Calvin enjoys playing tennis, cooking, and exploring the city
            of San Francisco.
        """),
    ),
    Member(
        'elu',
        'Eddie Lu',
        (),
        dedent("""
            Eddie grew up in Plainsboro, New Jersey. At UC Berkeley, he honed
            his interest in research, and was inspired by his mentors at The
            Klinman Group, where he studied soybean lipoxygenase-1 as an enzyme
            model to C-H bond activation and protein global/local interactions.
            After having earned his degree in Molecular and Cell Biology with
            an emphasis in Immunology, he plans to study glioblastomas and
            potential drug targets for immunotherapy with a lab at UCSF. He is
            excited to continue research and hopes to become an oncologist some
            day. In his free time, he enjoys photography and animals.
        """),
    ),
    Member(
        'mleone',
        'Michael Leone',
        (),
        dedent("""
            Michael is currently studying neurobiology in college. He works in
            a lab that explores how certain genes regulate the development of
            neurons. He enjoys science because it is constantly progressing and
            evolving and to be a part of it is incredibly exciting. Running
            experiments, collecting data, and then realizing that the data
            you’re holding may contribute to this advancement in science is a
            really cool feeling. He is a part of Sci-Fi because he wants more
            people to have the opportunity to experience that same feeling. A
            fun fact about Michael is that he’s played ice hockey for 16 years
            and is currently on the Cal Ice Hockey team.
        """),
    ),
    Member(
        'rmakwana',
        'Rikki Makwana',
        (),
        dedent("""
            Rikhil, or Rikki, moved around a few times throughout his
            childhood, but ended up settling in Yorba Linda, California, where
            his passion for biology and the other sciences flourished
            throughout middle school and high school. He is currently pursuing
            a degree in Molecular and Cell Biology at the University of
            California, Berkeley, whilst also finding time to volunteer at
            schools in the Oakland/Berkeley area where he teaches students
            about chemistry and ecology.
        """),
    ),
    Member(
        'sgriffin',
        'Sandon Griffin',
        ('Chief Executive Officer',),
        dedent("""
            Sandon grew up in Newport Beach, California. He developed an
            interest in the mind and brain during high school, which led him to
            pursue degrees in Psychology and Neurobiology at UC Berkeley.
            Currently, Sandon works at the Helen Wills Neuroscience Institute,
            where he studies how emotions are encoded in the human brain. In
            the future, he hopes to become a physician scientist and develop
            new brain-computer interface treatments. In his free time, Sandon
            enjoys carpentry, ice hockey, and playing with his cat.
        """),
    ),
    Member(
        'cswerdlick',
        'Chase Swerdlick',
        (),
        dedent("""
            Chase comes to us from the faraway town of Cromwell, CT. From an
            early age, he was consistently drawn to the uncertainty and
            certainty that came with science. He is currently pursuing a degree
            in Molecular and Cellular Neurobiology at UC Berkeley and hopes to
            attend medical school after he graduates in 2020. In his free time,
            Chase de-stresses by getting on the ice and shooting some hockey
            pucks.
        """)
    )
)


def home(request):
    return render(
        request,
        'home.html',
        {
            'full_title': 'Project SCIFI',
            'members': random.sample(MEMBERS, 4),
            'posts': blog.get_posts(per_page=5),
        },
    )
