from re import sub
from hashlib import md5

class FileHandler:
    def get_setting(self, key, accepted_min, accepted_max):
        """
        Etsii settings-tiedostosta sen rivin jossa 'key' on. Poistaa siltä riviltä kaikki
        kirjaimet ja symbolit (regex [^0-9] vastaa kaikkia ei-numeroita), jos saatu arvo on annettujen rajojen (accepted_min, accepted_max)
        välissä, palauttaa sen, muussa tapauksessa palauttaa Nonen.
        """
        try:
            settings = open("settings", "r")
        except FileNotFoundError:
            print("Error! Could not open the settings file")
            return None
        else:
            value = 0
            for line in settings:
                if key in line:
                    try:
                        value = int(sub("[^0-9]", "", line))
                    except ValueError:
                        print("Error! Could not read integer from the settings file")
                        return None
                    if value >= accepted_min and value <= accepted_max:
                        settings.close()
                        return value
            settings.close()
            return None

    def write_statistics(self, stats):
        """
        Tekee annetusta stats-listasta pilkuilla erotetun merkkijonon. Tekee merkkijonosta
        MD5-tiivisteen käyttämällä aikaleimaa suolana. Suolan käyttäminen estää jotenkuten tilastojen muokkaamisen
        käsin ja uuden MD5-tiivisteen laskemisen sen perusteella. Lopuksi yhdistää alkuperäisen merkkijonon ja tiivisteen puolipisteellä
        ja kirjoittaa sen tiedostoon statistics.
        """
        try:
            stats_file = open("statistics", 'a')
        except FileNotFoundError:
            print("Error! Could not open the statistics file")
        else:
            stats_text = ",".join(stats)
            hash_salt = stats[1].encode("utf-8")
            hashed = md5(stats_text.encode("utf-8") + hash_salt).hexdigest()
            stats_file.write(";".join((stats_text, hashed)))
            stats_file.write("\n")
            stats_file.close()

    def print_statistics(self):
        """
        Lukee rivejä statistics-tiedostosta, tarkistaa tilastoista lasketun MD5 tiivisteen ja vertaa sitä
        tilastoissa olevaan tiivisteeseen, jos tiivisteet ovat samat, tilastoja ei ole muutettu käsin ja ne lähetetään
        edelleen print_formatted_stats funktioon. Mikäli MD5-tarkastus epäonnistuu tulostaa varoituksen.
        """
        try:
            stats = open("statistics", "r")
        except FileNotFoundError:
            print("Error! Could not open the statistics file.")
        else:
            line_number = 1
            for line in stats.readlines():
                text_and_hash = line.split(";")
                stats_list = text_and_hash[0].split(",")
                hash_salt = stats_list[1].encode("utf-8")
                if md5(text_and_hash[0].encode("utf-8") + hash_salt).hexdigest() == text_and_hash[1].rstrip("\n"):
                    self.print_formatted_stats(stats_list)
                else:
                    print("Warning! MD5 check failed (modified statistics file) on line {}.".format(line_number))
                line_number += 1
            stats.close()

    def print_formatted_stats(self, stats):
        """
        Tulostaa annetun stats-listan terminaaliin muotoiltuna.
        """
        if stats[0] == "W":
            print("==============VICTORY==============")
        else:
            print("==============FAILURE==============")
        print("TIME: {}".format(stats[1]))
        print("GRID SIZE: {}x{}".format(stats[2], stats[3]))
        print("MINE COUNT: {}".format(stats[4]))
        print("ELAPSED TIME: {}:{}".format(stats[5].zfill(2), stats[6].zfill(2)))
        print("AMOUNT OF MOVES: {}".format(stats[7]))
