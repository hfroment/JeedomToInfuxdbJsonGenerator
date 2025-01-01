#ifndef MIXTRAVERSLOREMAINWINDOW_H
#define MIXTRAVERSLOREMAINWINDOW_H

#include <QMainWindow>

namespace Ui {
class MixtraVersLoreMainWindow;
}

class QFileInfo;

class JeedomToInfuxdbJsonGenerator : public QMainWindow
{
    Q_OBJECT

public:
    explicit JeedomToInfuxdbJsonGenerator(QWidget *parent = 0);
    ~JeedomToInfuxdbJsonGenerator();

protected:
    void dragEnterEvent(QDragEnterEvent *event);
    void dropEvent(QDropEvent *event);

private:
    Ui::MixtraVersLoreMainWindow *ui;

    void log(QString texte);
    void traiterFichier(QFileInfo& fileInfo);
    void traiterRepertoire(QFileInfo& fileInfo);

    enum
    {
        CommentIndex = 0,
        SubCommentIndex,
        DataTypeIndex,
        IdxIndex,
        JeedomIndexIndex
    };

};

#endif // MIXTRAVERSLOREMAINWINDOW_H
