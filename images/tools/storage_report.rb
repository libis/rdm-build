#!/usr/bin/env ruby

require 'dotenv/load'
require 'dataverse'
require 'fileutils'
require 'csv'

ENV['DATA_DIR'] ||= '/opt/data'
ENV['COLLECTION'] ||= ':root'
ENV['ORCID_FILE'] ||= File.join({ENV['DATA_DIR'], 'orcid.csv')
ENV['REPORTS_DIR'] ||= File.join(ENV['DATA_DIR'], 'reports')

FileUtils.mkdir_p(ENV['REPORTS_DIR'])

orcid_map = {}
CSV.foreach(ENV['ORCID_FILE']) do |row|
  orcid_map[row.last.downcase] = row.first.downcase
end

dv = Dataverse::Dataverse.id(ENV['COLLECTION'])

storage_map = {}
error_ds = []

puts "Collecting Datasets storage from Dataverse Collection '#{dv['name']}' ..."

root_dv.each_dataset do |ds|
  authors = ds.metadata['author']
  unr = nil
  authors.each do |author|
    break if author['authorIdentifierScheme'] == 'ORCID' && unr = orcid_map[author['authorIdentifier']]
  end
  unless unr
    puts "WARNING: Dataset #{ds.pid} does not have an author to contribute the storage to (not a known ORCID)."
    error_ds << ds.pid
    next
  end
  storage_map[unr] ||= 0
  storage_map[unr] += ds.size
end

now = DateTime.now

filepath = File.join(ENV['REPORTS_DIR'], "storage_#{now.strftime('%Y-%m-%d')}.csv")
File.open(filepath, 'wt') { |f| f.puts '"u-number","storage in bytes"'; storage_map.each { |unr,size| f.puts "#{unr},#{size}" } }

puts "Storage report '#{File.basename(filepath)}' written. #{storage_map.size} entries."

filepath = File.join(ENV['REPORTS_DIR'], "storage_#{now.strftime('%Y-%m-%d')}.errors")
File.open(filepath, 'wt') { |f| error_ds.each { |id| f.puts "#{id}" } }

puts "Storage errors report '#{File.basename(filepath)}' written. #{errors_ds.size} errors."
