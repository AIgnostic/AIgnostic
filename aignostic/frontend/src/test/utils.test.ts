import checkURL from "../app/utils";

describe('checkURL function', () => {
  it('should return true for valid URLs', () => {
    const validUrls = [
      'https://www.example.com',
      'http://example.com',
      'ftp://ftp.example.com',
      'https://subdomain.example.com/path/to/resource',
      'https://www.example.com:8080/path/to/resource',
      'https://example.co.uk',
      'http://example.com?search=test#anchor',
      'https://192.168.1.1',
      'https://www.example.com/path?query=value#fragment',
    ];

    validUrls.forEach((url) => {
      console.log(url);
      expect(checkURL(url)).toBe(true);
    });
  });

  it('should return false for invalid URLs', () => {
    const invalidUrls = [
      'htp://www.example.com', // Protocol typo
      '://www.example.com', // Missing protocol
      'http://', // Missing domain
      'http://256.256.256.256', // Invalid IP address format
      'www.example.com', // Missing protocol
      'http://example..com', // Double dots in domain
      'http://-example.com', // Domain starts with a hyphen
      'http://example#.com', // Invalid character in domain
      'ftp://.example.com', // Domain starts with a dot
      'http://%20example.com', // Invalid percent-encoded space
    ];

    invalidUrls.forEach((url) => {
      console.log(url);
      expect(checkURL(url)).toBe(false);
    });
  });
});
