#include "JeedomToInfuxdbJsonGenerator.h".h"
#include <QApplication>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    JeedomToInfuxdbJsonGenerator w;
    w.show();

    return a.exec();
}
