#!/usr/bin/env ruby

require 'dotenv/load'
require 'dataverse'
require 'fileutils'
require 'csv'

orcid_map = {}
CSV.foreach("#{ENV['DATA_DIR']}/orcid.csv") do |row|
  orcid_map[row.last.downcase] = row.first.downcase
end

root_dv = Dataverse::Dataverse.id('kul')

storage_map = {}
error_ds = []

root_dv.each_dataset do |ds|
  authors = ds.metadata['author']
  unr = nil
  authors.each do |author|
    break if author['authorIdentifierScheme'] == 'ORCID' && unr = orcid_map[author['authorIdentifier']]
  end
  unless unr
    error_ds << ds.pid
    next
  end
  storage_map[unr] ||= 0
  storage_map[unr] += ds.size
end

now = DateTime.now
filepath = "#{ENV['DATA_DIR']}/reports/storage-#{now.strftime('%Y-%m-%d')}.csv"
FileUtils.mkdir_p(File.dirname(filepath))
File.open(filepath, 'wt') { |f| storage_map.each { |unr,size| f.puts "#{unr},#{size}" } }

filepath = "#{ENV['DATA_DIR']}/reports/storage-#{now.strftime('%Y-%m-%d')}.errors"
File.open(filepath, 'wt') { |f| error_ds.each { |id| f.puts "#{id}" } }