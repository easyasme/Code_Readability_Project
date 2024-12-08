#! python3

from colored import fg

yellowish = fg(184)
pink = fg(183)
palegreen = fg(86)
blue = fg(45)
magenta = fg(164)

q1 = yellowish + "\
\t Files are a means to store data in a storage device."

q2 = pink + "\
\t An object is a region of storage that has a type and a value."

q3 = blue + "\
\n\t An expression is referentially transparent if it has no observable side effects,\
\n\t and therefore all functions used in that expression are pure.\
\n\t  - Ivan Cukic"

q4 = magenta + "\
\n\t For what shall it profit a man,\
\n\t if he shall gain the whole world but lose his soul?"

q5 = pink + "\
\n\t Well written scripts use absolute paths to executables."

q6 = palegreen + "\
\n\t You can't make somebody understand something if their salary\
\n\t depends upon them not understanding it.\
\n\t  - Upton Sinclair"

q7 = blue + "\
\n\t Any fool can write code that a computer can understand.\
\n\t Good programmers write code that humans can understand.\
\n\t - Martin Fowler"

q8 = pink + "\
\n\t When clients of a complex system are ignorant of how it works,\
\n\t yet happy with what it does, that says a lot about the design of the system.\
\n\t  - Scott Meyers"


qs = [q1, q2, q3 , q4, q5, q6, q7, q8]

for q in qs:
    print("\n" + q)
print()
