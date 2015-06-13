#!/usr/bin/ruby
require 'open-uri'
require 'nokogiri'
require 'mysql2'

sheet_id = '1lVrCb2kJr9XKkKKILSflfluB4wMSb7mQOOoVWbq-OUA'
url = "https://spreadsheets.google.com/feeds/cells/#{sheet_id}/od6/public/full"
content = open(url).read

def fix_date(date)
    date.split('.').reverse.join('-')
end

DB_USER = "brutarie"
DB_PASSWORD = "m!tItic@"
DB_HOST = "localhost"
DB_DATABASE = "maricorupti"
DB_TABLE = "dosare_corupti"

xmldoc = Nokogiri::XML(content)

cells = xmldoc.xpath('//gs:cell')

rows = {}

cells.each do |cell|
  current_row = cell['row'].to_i
  current_col = cell['col'].to_i

  rows[current_row] ||= {}
  rows[current_row][current_col] = cell.children.first.text.strip
end

client = Mysql2::Client.new(:host => DB_HOST, :username => DB_USER, :password => DB_PASSWORD, :db => DB_DATABASE)
client.query("use #{DB_DATABASE}")
#p rows.values

# Empty table
if rows.values.empty?
  exit
end
client.query("delete from #{DB_TABLE}")
client.query("ALTER TABLE #{DB_TABLE} AUTO_INCREMENT = 1")

# ESCAPING
rows.values[1..-1].each do |row|
  next if row.values[1..-1].all?(&:empty?)
  if client.escape(row[12].to_s) == 'TRUE'
    executare = 1
  else
    executare = 0
  end
  #p "insert into #{DB_TABLE} (porecla_dosar, nume, prenume, functie_publica, partid_1, partid_2, functie_secundara, fapta, data_condamnarii, durata_dosar, ani_inchisoare, executare, discount, motiv_discount, link_presa, descriere_fapta, observatii, prejudiciu, avere_recuperata, wiki_link, dosare_similare, img_url) values ('#{client.escape(row[1].to_s)}', '#{client.escape(row[2].to_s)}', '#{client.escape(row[3].to_s)}', '#{client.escape(row[4].to_s)}', '#{client.escape(row[5].to_s)}', '#{client.escape(row[6].to_s)}', '#{client.escape(row[7].to_s)}', '#{client.escape(row[8].to_s)}', '#{client.escape(fix_date(row[9].to_s))}', '#{client.escape(row[10].to_s)}', '#{client.escape(row[11].to_s)}', '#{executare}', '#{client.escape(row[13].to_s)}', '#{client.escape(row[14].to_s)}', '#{client.escape(row[15].to_s)}', '#{client.escape(row[16].to_s)}', '#{client.escape(row[17].to_s)}', '#{client.escape(row[18].to_s)}', '#{client.escape(row[19].to_s)}', '#{client.escape(row[20].to_s)}', '#{client.escape(row[21].to_s)}', '#{client.escape(row[22].to_s)}')"
  client.query("insert into #{DB_TABLE} (porecla_dosar, nume, prenume, functie_publica, partid_1, partid_2, functie_secundara, fapta, data_condamnarii, durata_dosar, ani_inchisoare, executare, discount, motiv_discount, link_presa, descriere_fapta, observatii, prejudiciu, avere_recuperata, wiki_link, dosare_similare, img_url, img_url_slider) values ('#{client.escape(row[1].to_s)}', '#{client.escape(row[2].to_s)}', '#{client.escape(row[3].to_s)}', '#{client.escape(row[4].to_s)}', '#{client.escape(row[5].to_s)}', '#{client.escape(row[6].to_s)}', '#{client.escape(row[7].to_s)}', '#{client.escape(row[8].to_s)}', '#{client.escape(fix_date(row[9].to_s))}', '#{client.escape(row[10].to_s)}', '#{client.escape(row[11].to_s)}', '#{executare}', '#{client.escape(row[13].to_s)}', '#{client.escape(row[14].to_s)}', '#{client.escape(row[15].to_s)}', '#{client.escape(row[16].to_s)}', '#{client.escape(row[17].to_s)}', '#{client.escape(row[18].to_s)}', '#{client.escape(row[19].to_s)}', '#{client.escape(row[20].to_s)}', '#{client.escape(row[21].to_s)}', '#{client.escape(row[22].to_s)}', '#{client.escape(row[23].to_s)}')")
end
