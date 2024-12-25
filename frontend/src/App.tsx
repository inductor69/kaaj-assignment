import React, { useState } from 'react';
import {
  ChakraProvider,
  Box,
  VStack,
  Input,
  Button,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Text,
  Heading,
  useToast,
  Spinner,
  Badge,
} from '@chakra-ui/react';
import { searchBusiness } from './services/api';
import { Business } from './types';

function App() {
  const [searchTerm, setSearchTerm] = useState('');
  const [business, setBusiness] = useState<Business | null>(null);
  const [loading, setLoading] = useState(false);
  const toast = useToast();

  const handleSearch = async () => {
    if (!searchTerm) {
      toast({
        title: 'Error',
        description: 'Please enter a business name',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    setLoading(true);
    try {
      const data = await searchBusiness(searchTerm);
      setBusiness(data);
      if (!data) {
        toast({
          title: 'No Results',
          description: 'No matching business found',
          status: 'info',
          duration: 3000,
          isClosable: true,
        });
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to fetch business details',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <ChakraProvider>
      <Box p={8}>
        <VStack spacing={8} align="stretch">
          <Heading>Florida Business Search</Heading>
          
          <Box display="flex" gap={4}>
            <Input
              placeholder="Enter business name"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              size="lg"
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  handleSearch();
                }
              }}
            />
            <Button
              colorScheme="blue"
              onClick={handleSearch}
              isLoading={loading}
              size="lg"
            >
              Search
            </Button>
          </Box>

          {loading && <Spinner size="xl" alignSelf="center" />}

          {business && (
            <Box overflowX="auto" borderWidth="1px" borderRadius="lg" p={4}>
              <Table variant="simple">
                <Thead>
                  <Tr>
                    <Th>Field</Th>
                    <Th>Information</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  <Tr>
                    <Td fontWeight="bold">Business Name</Td>
                    <Td>{business.name}</Td>
                  </Tr>
                  <Tr>
                    <Td fontWeight="bold">Status</Td>
                    <Td>
                      <Badge 
                        colorScheme={business.status.toLowerCase() === 'active' ? 'green' : 'red'}
                      >
                        {business.status}
                      </Badge>
                    </Td>
                  </Tr>
                  <Tr>
                    <Td fontWeight="bold">Filing Date</Td>
                    <Td>{business.filing_date || 'N/A'}</Td>
                  </Tr>
                  <Tr>
                    <Td fontWeight="bold">Registered Agent</Td>
                    <Td>
                      {business.registered_agent ? (
                        <VStack align="start" spacing={1}>
                          <Text>{business.registered_agent.name}</Text>
                          <Text fontSize="sm" color="gray.600">
                            {business.registered_agent.address}
                          </Text>
                        </VStack>
                      ) : (
                        'N/A'
                      )}
                    </Td>
                  </Tr>
                  <Tr>
                    <Td fontWeight="bold">Principals</Td>
                    <Td>
                      {business.principals && business.principals.length > 0 ? (
                        <VStack align="start" spacing={4}>
                          {business.principals.map((principal, index) => (
                            <Box key={index}>
                              <Text fontWeight="medium">{principal.name}</Text>
                              {principal.title && (
                                <Text fontSize="sm" color="gray.600">
                                  Title: {principal.title}
                                </Text>
                              )}
                              {principal.address && (
                                <Text fontSize="sm" color="gray.600">
                                  {principal.address}
                                </Text>
                              )}
                            </Box>
                          ))}
                        </VStack>
                      ) : (
                        'No principals listed'
                      )}
                    </Td>
                  </Tr>
                  <Tr>
                    <Td fontWeight="bold">Record Details</Td>
                    <Td>
                      <Text fontSize="sm" color="gray.600">
                        Created: {formatDate(business.created_at)}
                      </Text>
                      <Text fontSize="sm" color="gray.600">
                        Last Updated: {formatDate(business.updated_at)}
                      </Text>
                    </Td>
                  </Tr>
                </Tbody>
              </Table>
            </Box>
          )}
        </VStack>
      </Box>
    </ChakraProvider>
  );
}

export default App;
