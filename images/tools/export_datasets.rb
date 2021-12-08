#!/usr/bin/env ruby

require 'dotenv/load'
require 'dataverse'
require 'fileutils'

ENV['DATA_DIR'] ||= File.join('/', 'opt', 'data')
ENV['EXPORT_DIR'] ||= File.join(ENV['DATA_DIR'], 'exports')
FileUtils.mkdir_p(ENV['EXPORT_DIR'])

ENV['COLLECTION'] ||= ':root'

ENV['FROM_DATE_FILE'] ||= File.join(ENV['EXPORT_DIR'], 'last_export_date')

from_date = File.exist?(ENV['FROM_DATE_FILE']) ? Time.parse(File.read(ENV['FROM_DATE_FILE'])) : Time.new(2021)
to_date = Time.now

dv = Dataverse::Dataverse.id(ENV['COLLECTION'])

puts "Extracting Datasets from Dataverse Collection '#{dv['name']}'"
puts "published between #{from_date} and #{to_date} ..."

i = 0
dv.each_dataset do |ds|
  next unless ds.version(:published)
  next unless ds.published >= from_date
  next unless ds.published < to_date
  data = ds.export_metadata('rdm')
  filename = "#{ds['identifier']}.json"
  filepath = File.join(ENV['EXPORT_DIR'], filename)
  puts "#{filename}\t#{ds['persistentUrl']}\t#{ds.title(version: :published)}"
  File.open(filepath, 'wt') { |f| f.write JSON.pretty_generate(data) }
  i += 1
end

File.write(ENV['FROM_DATE_FILE'], to_date.to_s)

puts "-------------"
puts "#{i} datasets exported."
