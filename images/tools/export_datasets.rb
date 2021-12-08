#!/usr/bin/env ruby

require 'dotenv/load'
require 'dataverse'
require 'fileutils'
require 'date'

ENV['DATA_DIR'] ||= File.join('/', 'opt', 'data')
ENV['EXPORT_DIR'] ||= File.join(ENV['DATA_DIR'], 'exports')
FileUtils.mkdir_p(ENV['EXPORT_DIR'])

ENV['COLLECTION'] ||= 'rdr'

ENV['FROM_DATE_FILE'] ||= File.join(ENV['EXPORT_DIR'], 'last_export_date')

from_date = File.exist?(ENV['FROM_DATE_FILE']) ? Date.parse(File.read(ENV['FROM_DATE_FILE'])) : Date.new(2021)

puts "Extracting Datasets from Dataverse Collection '#{ENV['COLLECTION']}'"
puts "published between #{from_date} and #{Date.today} ..."

dv = Dataverse::Dataverse.id(ENV['COLLECTION'])
i = 0
dv.each_dataset do |ds|
  next unless ds.version(:published)
  next unless Date.parse(ds.publicationDate) >= from_date
  next unless Date.parse(ds.publicationDate) < Date.today
  data = ds.export_metadata('rdm')
  filename = "#{ds['identifier']}.json"
  filepath = File.join(ENV['EXPORT_DIR'], filename)
  puts "#{filename}\t#{ds['persistentUrl']}\t#{ds.metadata['title']}"
  File.open(filepath, 'wt') { |f| f.write JSON.pretty_generate(data) }
  i += 1
end

File.write(ENV['FROM_DATE_FILE'], Date.today.to_s)

puts "-------------"
puts "#{i} datasets exported."
