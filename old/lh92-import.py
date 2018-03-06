#!/usr/bin/env python3
import os
import datetime
import pywikibot
import logging
import lh92.read_zotero_csv
import lh92.create_wikipage
import lh92.create_filepage

class LH92:
    def __init__(self):
        return

    def read_csv(self, csv_file):
        """ read csv file
        """
        foo = lh92.read_zotero_csv.zotero_csv(csv_file)
        # fetch all csv data as they were exported from zotero
        #csv_data = foo.get_raw_csv_data()
        # fetch the data for all import sites, ready for the wiki
        csv_data = foo.get_prepared_csv_data()

        return csv_data

    def create_pages(self, csv_data):
        """ create one page for each row from csv file
        """
        creator = lh92.create_wikipage.create_wikipage()
        # begin range with 1 to skip csv head and end with +1
        for row in range(1, len(csv_data[1:])+1):
            #print(csv_data[row])
            # skip empty rows
            if csv_data[row]:
                #pagename = "SandKasten-%s" % (csv_data[row][0])
                # use signature attribute as title for wikipage
                pagename = "%s" % self.get_signature(csv_data, row)
                #TODO skip row if pagename is empty
                print("\n%s -- %s -- %s --" % \
                    (str(datetime.datetime.now()), \
                    row, str(pagename)))
                pagetext = self.convert_csv2pagetext(csv_data, row)
                comment = "test"
                creator.insert_text(pagename, pagetext, comment)
        return

    def get_signature(self, csv_data, row):
        """
        return the signature of an entry in the given row
        todo: return some value if empty
        """
        signature = ""
        for field in range(len(csv_data[0])):
            if csv_data[row][field]:
                #print("Feld: %s" % field)
                #print("%s: %s" % (csv_data[0][field], csv_data[row][field]))

                if csv_data[0][field] == "Signatur":
                    logging.info("Signatur: %s" % csv_data[row][field])
                    #print("Signatur: %s" % csv_data[row][field])
                    signature = csv_data[row][field]
        return signature


    def convert_csv2pagetext(self, csv_data, row):
        """
        change some csv fields before putting them into the wiki
        also file uploads will be triggered here
        """
        text = ""
        text += "__NOTOC__\n"

        for field in range(len(csv_data[0])):
                # print title
                if csv_data[0][field] == "Titel":
                    print("Titel: %s" % csv_data[row][field])
                    text += "== [[Titel::%s]] ==\n\n\n" % csv_data[row][field]

        for field in range(len(csv_data[0])):
                # separate authors
                if csv_data[0][field] == "Autor_in":
                    #print(csv_data[row][field])
                    for tag in csv_data[row][field][:]:
                        #print(tag)
                        text += "Autor_in: [[Autor_in::%s]]\n\n" % tag

        for field in range(len(csv_data[0])):
                # separate authors
                if csv_data[0][field] == "Date":
                    #print(csv_data[row][field])
                    text += "Datum: [[Date::%s]]\n\n" % csv_data[row][field]

        for field in range(len(csv_data[0])):
            if csv_data[row][field]:
                #print("Feld: %s" % field)
                #print("%s: %s" % (csv_data[0][field], csv_data[row][field]))
                # check if there is more than one file attachment
                if csv_data[0][field] == "Dateianhang":
                    # separate multiple files in several attributes
                    text += "=== Dateianhänge ===\n\n"
                    for filepath in csv_data[row][field][:]:
                        filename = ("%s" % os.path.basename(filepath))
                        # upload and link into page, if image exists
                        if os.path.isfile(filepath):
                            newrow = "[[%s::Datei:%s|x250px]]" % (csv_data[0][field], filename)
                            text += newrow
                            text += "\n\n"
                            self.upload_file(filename, filepath)
                            # upload ocr from jpg, if ocr exists
                            if os.path.splitext(filename)[1] == ".jpg":
                                filename_ocr = os.path.splitext(filename)[0] + ".txt"
                                #print("ocr filename %s": % filename_ocr)
                                filepath_ocr = os.path.splitext(filepath)[0] + ".txt"
                                #print("ocr filepath %s": % filepath_ocr)
                                if os.path.isfile(filepath_ocr):
                                    newrow = "[[%s::Datei:%s]]" % (csv_data[0][field], filename_ocr)
                                    text += newrow
                                    text += "\n\n"
                                    self.upload_file(filename_ocr, filepath_ocr)
                    text += "\n"
        text += "----\n\n"

        for field in range(len(csv_data[0])):
            if csv_data[row][field]:
                # use signature attribute as category for wikipage
                if csv_data[0][field] == "Signatur":
                    logging.info("Signatur: %s" % csv_data[row][field])
                    #print("Signatur: %s" % csv_data[row][field])
                    signature =  csv_data[row][field]
                    category = signature.split("-")
                    text += "[[Kategorie:%s-%s]]\n\n" % (category[0], category[1])

        for field in range(len(csv_data[0])):
            if csv_data[row][field]:
                # separate tags
                if csv_data[0][field] == "Tag":
                    text += "{{#set:\n"
                    #print(csv_data[row][field])
                    for tag in csv_data[row][field][:]:
                        #print(tag)
                        text += "|Tag=%s]]\n" % tag
                    text += "}}\n\n"

        # handle all other fields
        text += "{{#set:\n"
        for field in range(len(csv_data[0])):
            if csv_data[row][field]:
                if not csv_data[0][field] == "Tag" \
                and not csv_data[0][field] == "Dateianhang" \
                and not csv_data[0][field] == "Autor_in" \
                and not csv_data[0][field] == "Titel" \
                and not csv_data[0][field] == "Date" \
                and csv_data[0][field]:
                    newrow = "|%s=%s\n" % (csv_data[0][field], csv_data[row][field])
                    #print(newrow)
                    text += newrow
        text += "}}\n\n"
        return text


    def upload_file(self, filename, filepath):
        filepage = filename
        filepage_text = os.path.splitext(filename)[0]
        print(filepage)
        print(filepath)
        logging.info(filepath)
        print(filepage_text)
        f = lh92.create_filepage.create_filepage()
        f.upload_file(filepage, filepath, filepage_text)


if __name__ == "__main__":
    doit = LH92()
    csv = doit.read_csv("/data/zotero-export/lichtenhagen.csv")
    #csv = doit.read_csv("/data/zotero-export/debug.csv")
    #print(csv)
    doit.create_pages(csv)

