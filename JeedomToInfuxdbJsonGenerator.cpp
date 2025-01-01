#include <QDragEnterEvent>
#include <QUrl>
#include <QFile>
#include <QFileInfo>
#include <QtDebug>
#include <QDir>
#include <QMimeData>
#include <QJsonDocument>
#include <QJsonObject>
#include <QMimeData>

#include "JeedomToInfuxdbJsonGenerator.h"
#include "ui_JeedomToInfuxdbJsonGenerator.h"

JeedomToInfuxdbJsonGenerator::JeedomToInfuxdbJsonGenerator(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MixtraVersLoreMainWindow)
{
    ui->setupUi(this);
    setAcceptDrops(true);
}

JeedomToInfuxdbJsonGenerator::~JeedomToInfuxdbJsonGenerator()
{
    delete ui;
}
void JeedomToInfuxdbJsonGenerator::dragEnterEvent(QDragEnterEvent *event)
{
    //     if (event->mimeData()->hasFormat("text/plain"))
    event->acceptProposedAction();
}

void JeedomToInfuxdbJsonGenerator::dropEvent(QDropEvent *event)
{
    const QMimeData* data = event->mimeData();
    if (data->hasUrls())
    {
        QList<QUrl> urls = data->urls();
        if (urls.size() > 0)
        {
            for (int i = 0; i < urls.size(); i++)
            {
                QUrl url = urls.at(i);
                QFileInfo infos(url.toLocalFile());
                if (infos.isDir())
                {
                    traiterRepertoire(infos);
                }
                else
                {
                    traiterFichier(infos);
                }
            }
        }
    }
}
void JeedomToInfuxdbJsonGenerator::log(QString texte)
{
    ui->log->append(texte);
}
void JeedomToInfuxdbJsonGenerator::traiterFichier(QFileInfo& fileInfo)
{
    log(tr("Traitement du fichier %1").arg(fileInfo.fileName()));
    QFile fin(fileInfo.filePath());
    if (fin.open(QIODevice::ReadOnly))
    {
        QString contenu;
        // On parcours les lignes pour identifier l'entête
        QByteArray ligne;
        ligne = fin.readLine();
        QStringList entete;
        if (!ligne.isEmpty())
        {
            entete = QString::fromUtf8(ligne).split(';');
            ligne = fin.readLine();
        }
        QJsonDocument jsonDoc;
        QJsonObject rootJson;
        QString champCommentRemanent;
        while (!ligne.isEmpty())
        {
            QStringList champs = QString::fromUtf8(ligne).split(';');
            QJsonObject nodeJson;
            nodeJson[entete.at(IdxIndex).simplified()] = champs.at(IdxIndex).simplified();
            if (!champs.at(CommentIndex).simplified().isEmpty())
            {
                champCommentRemanent = champs.at(CommentIndex).simplified();
            }
            QString comment = champCommentRemanent;
            if (champs.at(SubCommentIndex).simplified().isEmpty())
            {
                comment.append(tr("-%1").arg(champs.at(DataTypeIndex).simplified()));
            }
            else
            {
                comment.append(tr("-%1").arg(champs.at(SubCommentIndex).simplified()));
            }
            nodeJson[entete.at(CommentIndex).simplified()] = comment;
            nodeJson[entete.at(DataTypeIndex).simplified()] = champs.at(DataTypeIndex).simplified();
            rootJson[champs.at(JeedomIndexIndex).simplified()] = nodeJson;
            qDebug() << champs;
            ligne = fin.readLine();
        }
        fin.close();
        jsonDoc.setObject(rootJson);
        log(jsonDoc.toJson());
        QFile fout(tr("%1/%2.json")
                       .arg(fileInfo.absolutePath())
                   .arg(fileInfo.baseName()));
        if (fout.open(QIODevice::WriteOnly))
        {
            fout.write(jsonDoc.toJson());
            fout.close();
        }
        else
        {
            log(tr("Impossible d'ovrir le fichier %1").arg(fout.fileName()));
        }
    }
    else
    {
        log(tr("Impossible d'ovrir le fichier %1").arg(fileInfo.filePath()));
    }
}


void JeedomToInfuxdbJsonGenerator::traiterRepertoire(QFileInfo& fileInfo)
{
    QDir repertoire(fileInfo.absoluteFilePath());
    repertoire.setFilter(QDir::AllDirs | QDir::Files | QDir::NoDotAndDotDot | QDir::NoSymLinks);
    //    QStringList filters;
    //    filters << "*.lcr";
    //    repertoire.setNameFilters(filters);
    repertoire.setSorting(QDir::Name);

    log(tr("Traitement du répertoire %1").arg(repertoire.absolutePath()));

    QFileInfoList list = repertoire.entryInfoList();
    for (int i = 0; i < list.size(); i++)
    {
        QFileInfo subFileInfo = list.at(i);
        if (subFileInfo.isDir())
        {
            traiterRepertoire(subFileInfo);
        }
        else
        {
            traiterFichier(subFileInfo);
        }
    }
}
